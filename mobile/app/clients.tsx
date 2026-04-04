import React, { useEffect, useState, useCallback, useMemo } from 'react';
import {
  View,
  Text,
  FlatList,
  TextInput,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import ClientCard from '../src/components/ClientCard';
import { fetchClients, ClientSummary } from '../src/services/api';

const TEAL = '#003235';
const EMERALD = '#008C6F';
const MINT = '#63D2B7';

export default function ClientsScreen() {
  const router = useRouter();
  const [clients, setClients] = useState<ClientSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');

  const load = useCallback(async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);
      setError(null);
      const data = await fetchClients();
      setClients(Array.isArray(data) ? data : []);
    } catch (err: any) {
      setError(err.message || 'Failed to load clients');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const filtered = useMemo(() => {
    if (!search.trim()) return clients;
    const q = search.toLowerCase();
    return clients.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.risk_profile?.toLowerCase().includes(q)
    );
  }, [clients, search]);

  if (loading && clients.length === 0) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={EMERALD} />
        <Text style={styles.loadingText}>Loading clients...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Clients</Text>
        <Text style={styles.headerCount}>{clients.length} total</Text>
      </View>

      {/* Search */}
      <View style={styles.searchWrap}>
        <TextInput
          style={styles.searchInput}
          placeholder="Search by name or risk profile..."
          placeholderTextColor="#999"
          value={search}
          onChangeText={setSearch}
        />
      </View>

      {/* Error */}
      {error && (
        <TouchableOpacity style={styles.errorBanner} onPress={() => load()}>
          <Text style={styles.errorText}>{error}</Text>
          <Text style={styles.errorRetry}>Tap to retry</Text>
        </TouchableOpacity>
      )}

      {/* List */}
      <FlatList
        data={filtered}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <ClientCard
            client={item}
            onPress={() => router.push(`/client/${item.id}`)}
          />
        )}
        contentContainerStyle={styles.list}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor={EMERALD} />
        }
        ListEmptyComponent={
          <View style={styles.emptyWrap}>
            <Text style={styles.emptyText}>
              {search ? 'No clients match your search' : 'No clients found'}
            </Text>
          </View>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: TEAL },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' },
  loadingText: { marginTop: 12, color: '#666', fontSize: 14 },

  header: {
    backgroundColor: TEAL,
    paddingHorizontal: 20,
    paddingBottom: 14,
    paddingTop: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  headerTitle: { color: '#FFF', fontSize: 20, fontWeight: '800' },
  headerCount: { color: MINT, fontSize: 13, fontWeight: '500' },

  searchWrap: {
    backgroundColor: '#F5F7FA',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  searchInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 15,
    color: '#1A1A1A',
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
  },

  errorBanner: {
    backgroundColor: '#FFEBEE',
    padding: 14,
    marginHorizontal: 16,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#E53935',
  },
  errorText: { color: '#C62828', fontSize: 13, fontWeight: '500' },
  errorRetry: { color: '#E53935', fontSize: 12, marginTop: 4, fontWeight: '600' },

  list: {
    paddingTop: 8,
    paddingBottom: 20,
    backgroundColor: '#F5F7FA',
    flexGrow: 1,
  },

  emptyWrap: { padding: 40, alignItems: 'center' },
  emptyText: { color: '#999', fontSize: 14, fontStyle: 'italic' },
});
