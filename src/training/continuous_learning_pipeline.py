#!/usr/bin/env python3
"""
Continuous Learning Pipeline
Automatically retrain XGBoost model with new security data and downloaded datasets
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContinuousLearningPipeline:
    """
    Continuous learning system for XGBoost compliance model
    - Ingests new data from multiple sources
    - Augments with downloaded security feeds
    - Retrains model incrementally
    - Validates performance before deployment
    """

    def __init__(self,
                 base_data_dir: str = "data/combined_compliance",
                 security_feeds_dir: str = "data/security_feeds",
                 models_dir: str = "results/models"):

        self.base_data_dir = Path(base_data_dir)
        self.security_feeds_dir = Path(security_feeds_dir)
        self.models_dir = Path(models_dir)

        # Create directories
        (self.models_dir / "continuous_learning").mkdir(parents=True, exist_ok=True)
        Path("data/new_samples").mkdir(parents=True, exist_ok=True)

        self.min_new_samples = 1000  # Minimum new samples before retraining
        self.performance_threshold = 0.95  # Minimum accuracy to deploy

    def ingest_new_data(self, source: str) -> pd.DataFrame:
        """
        Ingest new security data from various sources

        Args:
            source: Data source (file path, SIEM export, etc.)

        Returns:
            DataFrame with new samples
        """
        logger.info(f"Ingesting new data from: {source}")

        source_path = Path(source)

        if not source_path.exists():
            logger.error(f"Source not found: {source}")
            return pd.DataFrame()

        # Load based on file type
        if source_path.suffix == '.csv':
            df = pd.read_csv(source_path)
        elif source_path.suffix == '.json':
            df = pd.read_json(source_path)
        elif source_path.suffix == '.parquet':
            df = pd.read_parquet(source_path)
        else:
            logger.error(f"Unsupported file format: {source_path.suffix}")
            return pd.DataFrame()

        logger.info(f"  Loaded {len(df)} new samples")

        return df

    def augment_with_threat_intel(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Augment training data with threat intelligence from downloaded feeds
        """
        logger.info("Augmenting with threat intelligence...")

        # Load MITRE ATT&CK data
        mitre_techniques = self._load_mitre_techniques()

        # Load NIST NVD CVEs
        recent_cves = self._load_recent_cves()

        # Load malware indicators
        malware_indicators = self._load_malware_indicators()

        # Generate synthetic adversarial samples
        adversarial_samples = self._generate_adversarial_samples(
            df,
            mitre_techniques,
            recent_cves,
            malware_indicators
        )

        if len(adversarial_samples) > 0:
            logger.info(f"  Generated {len(adversarial_samples)} adversarial samples")
            df = pd.concat([df, adversarial_samples], ignore_index=True)

        return df

    def _load_mitre_techniques(self) -> List[Dict]:
        """Load MITRE ATT&CK techniques"""
        techniques = []

        mitre_dir = self.security_feeds_dir / "mitre_attack"
        if mitre_dir.exists():
            for json_file in mitre_dir.glob("*-techniques.json"):
                try:
                    with open(json_file, 'r') as f:
                        techniques.extend(json.load(f))
                except Exception as e:
                    logger.warning(f"Could not load MITRE data: {e}")

        logger.info(f"  Loaded {len(techniques)} MITRE techniques")
        return techniques

    def _load_recent_cves(self, days: int = 30) -> List[Dict]:
        """Load recent CVEs from NIST NVD"""
        cves = []

        nvd_dir = self.security_feeds_dir / "nist_nvd"
        if nvd_dir.exists():
            # Load most recent year
            current_year = datetime.now().year
            nvd_file = nvd_dir / f"nvdcve-{current_year}.json"

            if nvd_file.exists():
                try:
                    with open(nvd_file, 'r') as f:
                        data = json.load(f)
                        cves = data.get('CVE_Items', [])[:100]  # Top 100
                except Exception as e:
                    logger.warning(f"Could not load NVD data: {e}")

        logger.info(f"  Loaded {len(cves)} recent CVEs")
        return cves

    def _load_malware_indicators(self) -> List[Dict]:
        """Load malware indicators from threat feeds"""
        indicators = []

        malware_dir = self.security_feeds_dir / "malware_feeds"
        if malware_dir.exists():
            for json_file in malware_dir.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            indicators.extend(data[:50])  # Top 50 per feed
                except Exception as e:
                    logger.warning(f"Could not load malware data: {e}")

        logger.info(f"  Loaded {len(indicators)} malware indicators")
        return indicators

    def _generate_adversarial_samples(self,
                                     base_df: pd.DataFrame,
                                     mitre_techniques: List[Dict],
                                     cves: List[Dict],
                                     malware_indicators: List[Dict]) -> pd.DataFrame:
        """Generate adversarial training samples from threat intelligence"""

        samples = []

        # Use first row as template
        if len(base_df) == 0:
            return pd.DataFrame()

        template = base_df.iloc[0].to_dict()

        # Generate samples from MITRE techniques
        for technique in mitre_techniques[:20]:  # Top 20
            sample = template.copy()
            sample['log_message'] = f"{technique['name']}: {technique['description'][:100]}"
            sample['compliance_status'] = 'non_compliant'
            sample['control_id'] = 'SI-4'
            sample['control_family'] = 'System and Information Integrity'
            sample['timestamp'] = datetime.now().isoformat()
            samples.append(sample)

        # Generate samples from CVEs
        for cve in cves[:20]:  # Top 20
            cve_item = cve.get('cve', {})
            desc = cve_item.get('description', {}).get('description_data', [{}])[0].get('value', '')

            sample = template.copy()
            sample['log_message'] = f"Vulnerability detected: {desc[:100]}"
            sample['compliance_status'] = 'non_compliant'
            sample['control_id'] = 'RA-5'
            sample['control_family'] = 'Risk Assessment'
            samples.append(sample)

        # Generate samples from malware indicators
        for indicator in malware_indicators[:20]:  # Top 20
            if isinstance(indicator, dict):
                malware_name = indicator.get('malware', indicator.get('threat_type', 'unknown'))

                sample = template.copy()
                sample['log_message'] = f"Malware detected: {malware_name} - threat blocked by security system"
                sample['compliance_status'] = 'non_compliant'
                sample['control_id'] = 'SI-3'
                sample['control_family'] = 'System and Information Integrity'
                samples.append(sample)

        return pd.DataFrame(samples)

    def retrain_model(self,
                     new_data: pd.DataFrame,
                     model_name: str = "xgboost_continuous") -> Tuple[bool, Dict]:
        """
        Retrain model with new data

        Args:
            new_data: New training samples
            model_name: Name for saved model

        Returns:
            (success, metrics)
        """
        logger.info("Retraining model with new data...")

        # Load existing training data
        train_file = self.base_data_dir / "compliance_events_train.csv"
        if train_file.exists():
            existing_data = pd.read_csv(train_file)
            logger.info(f"  Loaded {len(existing_data)} existing samples")
        else:
            logger.warning("  No existing training data found")
            existing_data = pd.DataFrame()

        # Combine with new data
        if len(existing_data) > 0:
            combined_data = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            combined_data = new_data

        # Remove duplicates
        initial_count = len(combined_data)
        combined_data = combined_data.drop_duplicates(subset=['log_message'], keep='last')
        logger.info(f"  Removed {initial_count - len(combined_data)} duplicates")

        logger.info(f"  Total training samples: {len(combined_data)}")

        # Train model
        try:
            from models.xgboost_classifier import XGBoostClassifier

            classifier = XGBoostClassifier()

            # Prepare data
            X = combined_data.drop(columns=['compliance_status'])
            y = combined_data['compliance_status']

            # Remove leaky features
            for col in ['status_code', 'anomaly_label', 'severity']:
                if col in X.columns:
                    X = X.drop(columns=[col])

            # Train
            classifier.train(X, y)

            # Save model
            model_path = self.models_dir / "continuous_learning" / model_name
            classifier.save_model(str(model_path))

            logger.info(f"  Model saved to: {model_path}")

            # Evaluate on test set
            test_file = self.base_data_dir / "compliance_events_test.csv"
            if test_file.exists():
                test_df = pd.read_csv(test_file)

                # Remove leaky features from test
                X_test = test_df.drop(columns=['compliance_status'])
                y_test = test_df['compliance_status']

                for col in ['status_code', 'anomaly_label', 'severity']:
                    if col in X_test.columns:
                        X_test = X_test.drop(columns=[col])

                # Predict
                predictions, probabilities = classifier.predict(X_test)

                # Calculate metrics
                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

                y_true_binary = [1 if y == 'non_compliant' else 0 for y in y_test]
                y_pred_binary = [1 if y == 'non_compliant' else 0 for y in predictions]

                metrics = {
                    'accuracy': float(accuracy_score(y_true_binary, y_pred_binary)),
                    'precision': float(precision_score(y_true_binary, y_pred_binary)),
                    'recall': float(recall_score(y_true_binary, y_pred_binary)),
                    'f1_score': float(f1_score(y_true_binary, y_pred_binary)),
                    'training_samples': len(combined_data),
                    'new_samples_added': len(new_data),
                    'timestamp': datetime.now().isoformat()
                }

                # Save metrics
                metrics_file = model_path / "metrics.json"
                with open(metrics_file, 'w') as f:
                    json.dump(metrics, f, indent=2)

                logger.info(f"  Accuracy: {metrics['accuracy']:.2%}")
                logger.info(f"  Precision: {metrics['precision']:.2%}")
                logger.info(f"  Recall: {metrics['recall']:.2%}")

                # Check if performance meets threshold
                if metrics['accuracy'] >= self.performance_threshold:
                    logger.info("  ✓ Performance meets deployment threshold")
                    return True, metrics
                else:
                    logger.warning(f"  ✗ Performance below threshold ({self.performance_threshold:.2%})")
                    return False, metrics

            else:
                logger.warning("  No test set available for validation")
                return True, {'training_samples': len(combined_data)}

        except Exception as e:
            logger.error(f"  ✗ Training failed: {e}")
            return False, {'error': str(e)}

    def deploy_model(self, model_name: str = "xgboost_continuous"):
        """Deploy retrained model to production"""
        logger.info("Deploying model to production...")

        source_path = self.models_dir / "continuous_learning" / model_name
        target_path = self.models_dir / "xgboost_production"

        if not source_path.exists():
            logger.error(f"Source model not found: {source_path}")
            return False

        # Backup current production model
        if target_path.exists():
            backup_path = self.models_dir / f"xgboost_production_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(target_path, backup_path)
            logger.info(f"  Backed up current model to: {backup_path}")

        # Deploy new model
        shutil.copytree(source_path, target_path, dirs_exist_ok=True)
        logger.info(f"  ✓ Deployed model to: {target_path}")

        return True

    def run_pipeline(self, new_data_sources: List[str], auto_deploy: bool = False) -> Dict:
        """
        Run complete continuous learning pipeline

        Args:
            new_data_sources: List of paths to new data
            auto_deploy: Automatically deploy if performance is good

        Returns:
            Pipeline execution summary
        """
        logger.info("\n" + "="*100)
        logger.info("CONTINUOUS LEARNING PIPELINE")
        logger.info("="*100 + "\n")

        summary = {
            'start_time': datetime.now().isoformat(),
            'data_sources': new_data_sources,
            'steps': []
        }

        # Step 1: Ingest new data
        all_new_data = []
        for source in new_data_sources:
            df = self.ingest_new_data(source)
            if len(df) > 0:
                all_new_data.append(df)

        if not all_new_data:
            logger.error("No new data ingested")
            summary['status'] = 'failed'
            summary['error'] = 'No new data'
            return summary

        combined_new_data = pd.concat(all_new_data, ignore_index=True)
        summary['steps'].append({
            'step': 'ingest',
            'samples': len(combined_new_data)
        })

        # Step 2: Augment with threat intel
        augmented_data = self.augment_with_threat_intel(combined_new_data)
        summary['steps'].append({
            'step': 'augment',
            'samples': len(augmented_data),
            'added': len(augmented_data) - len(combined_new_data)
        })

        # Check minimum samples
        if len(augmented_data) < self.min_new_samples:
            logger.warning(f"Insufficient new samples ({len(augmented_data)} < {self.min_new_samples})")
            summary['status'] = 'skipped'
            summary['reason'] = 'Insufficient samples'
            return summary

        # Step 3: Retrain model
        success, metrics = self.retrain_model(augmented_data)
        summary['steps'].append({
            'step': 'retrain',
            'success': success,
            'metrics': metrics
        })

        # Step 4: Deploy if successful and auto-deploy enabled
        if success and auto_deploy:
            deployed = self.deploy_model()
            summary['steps'].append({
                'step': 'deploy',
                'success': deployed
            })
            summary['status'] = 'deployed'
        elif success:
            summary['status'] = 'trained'
            summary['message'] = 'Model trained but not deployed (auto_deploy=False)'
        else:
            summary['status'] = 'failed'
            summary['message'] = 'Training succeeded but performance below threshold'

        summary['end_time'] = datetime.now().isoformat()

        # Save summary
        summary_file = self.models_dir / "continuous_learning" / f"pipeline_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info("\n" + "="*100)
        logger.info(f"PIPELINE COMPLETE: {summary['status'].upper()}")
        logger.info("="*100 + "\n")

        return summary


def main():
    """Test continuous learning pipeline"""
    pipeline = ContinuousLearningPipeline()

    # Simulate new data sources
    new_sources = [
        "data/combined_compliance/compliance_events_test.csv"  # Use test data as example
    ]

    # Run pipeline
    summary = pipeline.run_pipeline(new_sources, auto_deploy=False)

    print("\n" + "="*100)
    print("PIPELINE SUMMARY")
    print("="*100)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
