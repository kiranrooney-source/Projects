import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  ScrollView,
} from 'react-native';
import ApiService from '../services/api';

export default function QueryScreen({ navigation, route }) {
  const { serverUrl, database } = route.params;
  const [requirements, setRequirements] = useState('');
  const [loading, setLoading] = useState(false);

  const handleExecuteQuery = async () => {
    if (!requirements.trim()) {
      Alert.alert('Error', 'Please enter your requirements');
      return;
    }

    setLoading(true);
    try {
      const result = await ApiService.executeQuery(serverUrl, requirements, database);
      navigation.navigate('Results', { result, requirements, database });
    } catch (error) {
      Alert.alert('Query Failed', error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Query Requirements</Text>
        
        <View style={styles.infoContainer}>
          <Text style={styles.infoLabel}>Database:</Text>
          <Text style={styles.infoValue}>{database}</Text>
        </View>

        <Text style={styles.label}>Enter your requirements:</Text>
        <TextInput
          style={styles.textArea}
          value={requirements}
          onChangeText={setRequirements}
          placeholder="Describe what you want to query (e.g., Find all active users from last month)"
          multiline
          numberOfLines={6}
          textAlignVertical="top"
        />

        <TouchableOpacity
          style={styles.button}
          onPress={handleExecuteQuery}
          disabled={loading}
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>Execute Query</Text>
          )}
        </TouchableOpacity>

        <View style={styles.examplesContainer}>
          <Text style={styles.examplesTitle}>Example Requirements:</Text>
          <Text style={styles.example}>• Find all customers who placed orders last week</Text>
          <Text style={styles.example}>• Show total sales by product category</Text>
          <Text style={styles.example}>• List inactive users from the past 30 days</Text>
          <Text style={styles.example}>• Get inventory levels below minimum stock</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  card: {
    backgroundColor: '#fff',
    margin: 20,
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
    marginBottom: 20,
    color: '#333',
  },
  infoContainer: {
    flexDirection: 'row',
    marginBottom: 20,
    padding: 10,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  infoLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#666',
  },
  infoValue: {
    fontSize: 16,
    marginLeft: 10,
    color: '#333',
    fontWeight: '500',
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#333',
  },
  textArea: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginBottom: 20,
    backgroundColor: '#fff',
    minHeight: 120,
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
  examplesContainer: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
  },
  examplesTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#333',
  },
  example: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
    lineHeight: 20,
  },
});