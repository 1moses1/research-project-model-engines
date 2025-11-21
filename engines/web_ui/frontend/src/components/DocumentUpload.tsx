import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { useWebSocket } from '@/hooks/useWebSocket';
import { UploadedFile } from '@/types';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8006';

export const DocumentUploadBox: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const { subscribe, isConnected } = useWebSocket();

  useEffect(() => {
    // Listen for upload progress updates via WebSocket
    const unsubscribe = subscribe('upload_progress', (data: any) => {
      updateFileStatus(data.filename, {
        status: data.status,
        progress: data.status === 'processing' ? 100 : data.progress || 0,
        extractedControls: data.extracted_controls,
        error: data.error
      });
    });

    return unsubscribe;
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    onDrop: async (acceptedFiles) => {
      for (const file of acceptedFiles) {
        await uploadDocument(file);
      }
    }
  });

  const uploadDocument = async (file: File) => {
    const fileObj: UploadedFile = {
      name: file.name,
      size: file.size,
      status: 'uploading',
      progress: 0
    };

    setFiles(prev => [...prev, fileObj]);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_name', 'Rwanda Demo Corp');
    formData.append('framework', 'Rwanda-NCSA');

    try {
      const response = await axios.post(`${API_URL}/api/v3/documents/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            updateFileStatus(file.name, { status: 'uploading', progress });
          }
        }
      });

      // Document uploaded, now processing
      updateFileStatus(file.name, { status: 'processing', progress: 100 });

      // Processing updates will come via WebSocket

    } catch (error: any) {
      updateFileStatus(file.name, {
        status: 'error',
        error: error.message || 'Upload failed'
      });
    }
  };

  const updateFileStatus = (fileName: string, updates: Partial<UploadedFile>) => {
    setFiles(prev => prev.map(f =>
      f.name === fileName ? { ...f, ...updates } : f
    ));
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Upload className="h-5 w-5" />
          Company Policy Documents Upload
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Upload policy documents for compliance auditing (PDF, DOCX, XLSX)
        </p>
      </CardHeader>
      <CardContent>
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
          {isDragActive ? (
            <p className="text-blue-600">Drop the files here ...</p>
          ) : (
            <div>
              <p className="text-lg font-medium mb-2">
                Drag & drop policy documents here
              </p>
              <p className="text-sm text-gray-500 mb-4">
                or click to browse (PDF, DOCX, XLSX)
              </p>
              <Button variant="outline">Select Files</Button>
            </div>
          )}
        </div>

        {/* Connection Status */}
        <div className="mt-4 flex items-center gap-2 text-sm">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-gray-600">
            {isConnected ? 'Connected to server' : 'Disconnected'}
          </span>
        </div>

        {/* Uploaded Files List */}
        {files.length > 0 && (
          <div className="mt-6 space-y-3">
            <h3 className="font-semibold text-sm text-gray-700">Uploaded Files</h3>
            {files.map((file, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-gray-500" />
                    <div>
                      <p className="font-medium">{file.name}</p>
                      <p className="text-sm text-gray-500">
                        {(file.size / 1024).toFixed(2)} KB
                      </p>
                    </div>
                  </div>
                  {file.status === 'completed' && (
                    <CheckCircle className="h-5 w-5 text-green-500" />
                  )}
                  {file.status === 'error' && (
                    <AlertCircle className="h-5 w-5 text-red-500" />
                  )}
                </div>

                {file.status === 'uploading' && (
                  <div>
                    <Progress value={file.progress} className="mb-1" />
                    <p className="text-sm text-gray-600">Uploading... {file.progress}%</p>
                  </div>
                )}

                {file.status === 'processing' && (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
                    <p className="text-sm text-blue-600">
                      Processing with LLM... Extracting controls
                    </p>
                  </div>
                )}

                {file.status === 'completed' && (
                  <p className="text-sm text-green-600">
                    ✓ Processing complete! Extracted {file.extractedControls || 0} controls
                  </p>
                )}

                {file.status === 'error' && (
                  <p className="text-sm text-red-600">✗ {file.error}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
