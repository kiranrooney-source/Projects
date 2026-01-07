import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import ApiService from '../services/api';

export default function HomeScreen({ navigation, route }) {
  const { serverUrl } = route.params;
  const [databases, setDatabases] = useState([]);
  const [selectedDatabase, setSelectedDatabase] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDatabases();
  }, []);

  const loadDatabases = async () => {
    try {
      const dbList = await ApiService.getDatabases(serverUrl);
      setDatabases(dbList.databases || []);
      if (dbList.databases && dbList.databases.length > 0) {
        setSelectedDatabase(dbList.databases[0]);
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to load databases');
    } finally {
      setLoading(false);
    }
  };

  const handleExecuteQuery = () => {
    if (!selectedDatabase) {
      Alert.alert('Error', 'Please select a database');
      return;
    }
    navigation.navigate('Query', { serverUrl, database: selectedDatabase });
  };

  const handleLogout = async () => {
    await ApiService.removeToken();
    navigation.navigate('Login');
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#007AFF" />
        <Text style={styles.loadingText}>Loading databases...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Select Database</Text>
        
        <View style={styles.pickerContainer}>
          <Picker
            selectedValue={selectedDatabase}
            onValueChange={setSelectedDatabase}
            style={styles.picker}
          >
            {databases.map((db, index) => (
              <Picker.Item key={index} label={db} value={db} />
            ))}
          </Picker>
        </View>

        <TouchableOpacity
          style={styles.button}
          onPress={handleExecuteQuery}
          disabled={!selectedDatabase}
        >
          <Text style={styles.buttonText}>Execute Query</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.logoutButton]}
          onPress={handleLogout}
        >
          <Text style={styles.buttonText}>Logout</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 20,
    justifyContent: 'center',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  card: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 30,
    color: '#333',
  },
  pickerContainer: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    marginBottom: 20,
  },
  picker: {
    height: 50,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  logoutButton: {
    backgroundColor: '#FF3B30',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});