import React from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
} from 'react-native';

export default function ResultsScreen({ navigation, route }) {
  const { result, requirements, database } = route.params;

  const handleNewQuery = () => {
    navigation.navigate('Query', { 
      serverUrl: route.params.serverUrl, 
      database 
    });
  };

  const renderQueryResult = (query, index) => (
    <View key={index} style={styles.queryContainer}>
      <Text style={styles.queryTitle}>Generated Query {index + 1}:</Text>
      <Text style={styles.queryText}>{query.sql}</Text>
      
      {query.results && (
        <View style={styles.resultsContainer}>
          <Text style={styles.resultsTitle}>Results:</Text>
          <ScrollView horizontal style={styles.tableContainer}>
            <View>
              {query.results.map((row, rowIndex) => (
                <View key={rowIndex} style={styles.tableRow}>
                  {Object.entries(row).map(([key, value], colIndex) => (
                    <View key={colIndex} style={styles.tableCell}>
                      <Text style={styles.tableCellText}>
                        {rowIndex === 0 ? key : String(value)}
                      </Text>
                    </View>
                  ))}
                </View>
              ))}
            </View>
          </ScrollView>
        </View>
      )}
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.title}>Query Results</Text>
        
        <View style={styles.infoContainer}>
          <Text style={styles.infoLabel}>Database:</Text>
          <Text style={styles.infoValue}>{database}</Text>
        </View>

        <View style={styles.requirementsContainer}>
          <Text style={styles.requirementsTitle}>Your Requirements:</Text>
          <Text style={styles.requirementsText}>{requirements}</Text>
        </View>

        {result.queries && result.queries.map((query, index) => 
          renderQueryResult(query, index)
        )}

        <TouchableOpacity
          style={styles.button}
          onPress={handleNewQuery}
        >
          <Text style={styles.buttonText}>New Query</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.homeButton]}
          onPress={() => navigation.navigate('Home')}
        >
          <Text style={styles.buttonText}>Back to Home</Text>
        </TouchableOpacity>
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
    marginBottom: 15,
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
  requirementsContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#e3f2fd',
    borderRadius: 8,
  },
  requirementsTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#1976d2',
  },
  requirementsText: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  queryContainer: {
    marginBottom: 20,
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  queryTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#333',
  },
  queryText: {
    fontSize: 14,
    fontFamily: 'monospace',
    backgroundColor: '#2d3748',
    color: '#fff',
    padding: 10,
    borderRadius: 4,
    marginBottom: 15,
  },
  resultsContainer: {
    marginTop: 10,
  },
  resultsTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 10,
    color: '#333',
  },
  tableContainer: {
    backgroundColor: '#fff',
    borderRadius: 4,
    borderWidth: 1,
    borderColor: '#ddd',
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  tableCell: {
    padding: 8,
    minWidth: 100,
    borderRightWidth: 1,
    borderRightColor: '#eee',
  },
  tableCellText: {
    fontSize: 12,
    color: '#333',
  },
  button: {
    backgroundColor: '#007AFF',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 10,
  },
  homeButton: {
    backgroundColor: '#34C759',
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
  },
});