const API_BASE_URL = 'http://localhost:8000';

class ApiClient {
  async uploadFile(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  async startMigration(file: File, config: any) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('config', JSON.stringify(config));

    const response = await fetch(`${API_BASE_URL}/migrate/start`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to start migration');
    }

    return response.json();
  }

  async getMigrationStatus(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/migrate/status/${sessionId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get status');
    }

    return response.json();
  }

  async getMigrationResults(sessionId: string) {
    const response = await fetch(`${API_BASE_URL}/migrate/results/${sessionId}`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to get results');
    }

    return response.json();
  }

  async makeDecision(sessionId: string, decision: 'accept' | 'reject' | 'manual', candidateId?: string) {
    const response = await fetch(`${API_BASE_URL}/migrate/decision`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        decision,
        candidate_id: candidateId,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to submit decision');
    }

    return response.json();
  }
}

export const api = new ApiClient();
