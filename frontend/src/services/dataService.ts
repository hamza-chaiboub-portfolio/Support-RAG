import apiClient from './api';

export interface UploadResponse {
  signal: string;
  file_id: string;
  asset_id: number;
  filename: string;
  size: number;
}

export interface ProcessResponse {
  signal: string;
  task_id: string;
  status: string;
}

const DEFAULT_PROJECT_ID = 1;

export const dataService = {
  uploadFile: async (file: File, projectId: number = DEFAULT_PROJECT_ID): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<UploadResponse>(
      `/data/upload/${projectId}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  processAsset: async (
    assetId: number, 
    projectId: number = DEFAULT_PROJECT_ID,
    chunkSize: number = 512,
    overlapSize: number = 50
  ): Promise<ProcessResponse> => {
    const response = await apiClient.post<ProcessResponse>(
      `/data/process/${projectId}`,
      null,
      {
        params: {
          asset_id: assetId,
          chunk_size: chunkSize,
          overlap_size: overlapSize,
        },
      }
    );
    return response.data;
  },
};
