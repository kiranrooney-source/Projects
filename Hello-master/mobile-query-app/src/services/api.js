import * as SecureStore from 'expo-secure-store';

const API_BASE_URL = 'http://localhost:5000';

class ApiService {
  async saveToken(token) {
    await SecureStore.setItemAsync('auth_token', token);
  }

  async getToken() {
    return await SecureStore.getItemAsync('auth_token');
  }

  async removeToken() {
    await SecureStore.deleteItemAsync('auth_token');
  }

  async authenticate(serverUrl, username, password) {
    const response = await fetch(`${serverUrl}/auth`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Authentication failed');
    }

    const data = await response.json();
    await this.saveToken(data.token);
    return data;
  }

  async getDatabases(serverUrl) {
    const token = await this.getToken();
    const response = await fetch(`${serverUrl}/databases`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch databases');
    }

    return await response.json();
  }

  async executeQuery(serverUrl, requirements, database) {
    const token = await this.getToken();
    const response = await fetch(`${serverUrl}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ requirements, database }),
    });

    if (!response.ok) {
      throw new Error('Query execution failed');
    }

    return await response.json();
  }

  async checkHealth(serverUrl) {
    const response = await fetch(`${serverUrl}/health`);
    return response.ok;
  }
}

export default new ApiService();