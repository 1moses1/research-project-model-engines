"""
Streaming Pipeline Service
Processes events and sends to ENGINE 3 (classification) and ENGINE 4 (decision)
"""

from typing import Dict, List
import asyncio
import httpx
from datetime import datetime


class StreamingPipeline:
    """Streaming pipeline for event processing"""

    def __init__(self, engine3_url: str, engine4_url: str):
        self.engine3_url = engine3_url
        self.engine4_url = engine4_url

        # Pipeline state
        self.active = True
        self.event_queue = asyncio.Queue()
        self.batch_queue = []
        self.batch_size = 10
        self.batch_timeout = 5  # seconds

        # Statistics
        self.stats = {
            "total_collected": 0,
            "total_parsed": 0,
            "total_classified": 0,
            "total_failed": 0,
            "events_per_second": 0.0,
            "system_logs": 0,
            "application_logs": 0,
            "network_logs": 0,
            "security_logs": 0,
            "database_logs": 0,
            "web_logs": 0,
        }

        self.start_time = datetime.now()

        # Start background batch processor
        asyncio.create_task(self._batch_processor())

    def is_active(self) -> bool:
        """Check if pipeline is active"""
        return self.active

    async def process_event(self, event: Dict):
        """
        Process single event through pipeline

        Steps:
        1. Add to queue
        2. Send to ENGINE 3 for classification
        3. Send to ENGINE 4 for decision/scoring
        """
        try:
            # Update stats
            self.stats["total_collected"] += 1
            self.stats["total_parsed"] += 1

            # Update source-specific stats
            source = event.get("source", "unknown")
            if source in self.stats:
                self.stats[source] += 1

            # Add to batch queue
            self.batch_queue.append(event)

            # If batch is full, process immediately
            if len(self.batch_queue) >= self.batch_size:
                await self._process_batch()

            # Calculate events per second
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if elapsed > 0:
                self.stats["events_per_second"] = self.stats["total_collected"] / elapsed

        except Exception as e:
            print(f"⚠️ Event processing error: {str(e)}")
            self.stats["total_failed"] += 1

    async def process_batch(self, events: List[Dict]):
        """
        Process batch of events

        Args:
            events: List of events to process
        """
        try:
            # Update stats
            self.stats["total_collected"] += len(events)
            self.stats["total_parsed"] += len(events)

            for event in events:
                source = event.get("source", "unknown")
                if source in self.stats:
                    self.stats[source] += 1

            # Send batch to ENGINE 3 for classification
            await self._classify_batch(events)

            # Calculate events per second
            elapsed = (datetime.now() - self.start_time).total_seconds()
            if elapsed > 0:
                self.stats["events_per_second"] = self.stats["total_collected"] / elapsed

        except Exception as e:
            print(f"⚠️ Batch processing error: {str(e)}")
            self.stats["total_failed"] += len(events)

    async def _batch_processor(self):
        """Background task to process batches periodically"""
        while self.active:
            await asyncio.sleep(self.batch_timeout)

            if self.batch_queue:
                await self._process_batch()

    async def _process_batch(self):
        """Process accumulated batch"""
        if not self.batch_queue:
            return

        batch = self.batch_queue[:self.batch_size]
        self.batch_queue = self.batch_queue[self.batch_size:]

        print(f"📊 Processing batch of {len(batch)} events")

        # Send to ENGINE 3 for classification
        await self._classify_batch(batch)

    async def _classify_batch(self, events: List[Dict]):
        """
        Send batch to ENGINE 3 for classification

        Args:
            events: List of events
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Prepare batch for ENGINE 3
                classification_requests = []

                for event in events:
                    classification_requests.append({
                        "log_message": event.get("log_message", ""),
                        "user": event.get("user"),
                        "ip_address": event.get("ip_address"),
                        "resource": event.get("resource"),
                        "action": event.get("action"),
                        "status_code": event.get("status_code"),
                        "timestamp": event.get("timestamp"),
                        "source": event.get("source"),
                    })

                # Send to ENGINE 3 batch endpoint
                try:
                    response = await client.post(
                        f"{self.engine3_url}/classify/batch",
                        json={"events": classification_requests},
                        timeout=30.0
                    )

                    if response.status_code == 200:
                        classifications = response.json().get("classifications", [])

                        # Send each classified event to ENGINE 4
                        for event, classification in zip(events, classifications):
                            await self._send_to_engine4(event, classification)

                        self.stats["total_classified"] += len(classifications)
                        print(f"✅ Classified {len(classifications)} events")

                    else:
                        print(f"⚠️ ENGINE 3 error: {response.status_code}")
                        self.stats["total_failed"] += len(events)

                except httpx.ConnectError:
                    print(f"⚠️ ENGINE 3 not available, skipping classification")
                except httpx.TimeoutException:
                    print(f"⚠️ ENGINE 3 timeout")
                except Exception as e:
                    print(f"⚠️ ENGINE 3 request error: {str(e)}")

        except Exception as e:
            print(f"⚠️ Classification batch error: {str(e)}")

    async def _send_to_engine4(self, event: Dict, classification: Dict):
        """
        Send classified event to ENGINE 4 for decision/scoring

        Args:
            event: Original event
            classification: Classification result from ENGINE 3
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Prepare event for ENGINE 4
                decision_request = {
                    "event_id": event.get("event_id"),
                    "log_message": event.get("log_message"),
                    "user": event.get("user"),
                    "ip_address": event.get("ip_address"),
                    "resource": event.get("resource"),
                    "action": event.get("action"),
                    "status_code": event.get("status_code"),
                    "timestamp": event.get("timestamp"),
                    "source": event.get("source"),
                    "severity": event.get("severity"),
                    # Add classification results
                    "prediction": classification.get("prediction"),
                    "confidence": classification.get("confidence"),
                    "probabilities": classification.get("probabilities"),
                }

                # Send to ENGINE 4
                try:
                    response = await client.post(
                        f"{self.engine4_url}/process/event",
                        json=decision_request,
                        timeout=10.0
                    )

                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ ENGINE 4 processed: {event.get('event_id')} -> {result.get('route_decision')}")
                    else:
                        print(f"⚠️ ENGINE 4 error: {response.status_code}")

                except httpx.ConnectError:
                    print(f"⚠️ ENGINE 4 not available")
                except httpx.TimeoutException:
                    print(f"⚠️ ENGINE 4 timeout")
                except Exception as e:
                    print(f"⚠️ ENGINE 4 request error: {str(e)}")

        except Exception as e:
            print(f"⚠️ ENGINE 4 send error: {str(e)}")

    def get_stats(self) -> Dict:
        """Get pipeline statistics"""
        return self.stats.copy()

    async def shutdown(self):
        """Shutdown pipeline gracefully"""
        print("🛑 Shutting down streaming pipeline...")
        self.active = False

        # Process remaining events in queue
        if self.batch_queue:
            print(f"📊 Processing final batch of {len(self.batch_queue)} events")
            await self._process_batch()

        print("✅ Pipeline shutdown complete")
