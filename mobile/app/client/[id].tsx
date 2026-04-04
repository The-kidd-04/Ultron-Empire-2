import React, { useEffect, useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { fetchClientById, ClientDetail } from '../../src/services/api';
import { formatINR, formatDate, formatPercent } from '../../src/utils/format';

const TEAL = '#003235';
const EMERALD = '#008C6F';
const MINT = '#63D2B7';

export default function ClientDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const [client, setClient] = useState<ClientDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(
    async (isRefresh = false) => {
      if (!id) return;
      try {
        if (isRefresh) setRefreshing(true);
        else setLoading(true);
        setError(null);
        const data = await fetchClientById(id);
        setClient(data);
      } catch (err: any) {
        setError(err.message || 'Failed to load client details');
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [id]
  );

  useEffect(() => {
    load();
  }, [load]);

  if (loading && !client) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={EMERALD} />
        <Text style={styles.loadingText}>Loading client details...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backBtn}>
          <Text style={styles.backText}>{'\u2190'} Back</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle} numberOfLines={1}>
          {client?.name || 'Client'}
        </Text>
      </View>

      <ScrollView
        style={styles.body}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => load(true)} tintColor={EMERALD} />
        }
      >
        {error && (
          <TouchableOpacity style={styles.errorBanner} onPress={() => load()}>
            <Text style={styles.errorText}>{error}</Text>
            <Text style={styles.errorRetry}>Tap to retry</Text>
          </TouchableOpacity>
        )}

        {client && (
          <>
            {/* Summary Card */}
            <View style={styles.summaryCard}>
              <View style={styles.summaryRow}>
                <SummaryItem label="AUM" value={formatINR(client.aum_cr)} />
                <SummaryItem label="Risk Profile" value={client.risk_profile || '--'} />
              </View>
              <View style={styles.summaryRow}>
                <SummaryItem label="Joined" value={formatDate(client.joined_date)} />
                <SummaryItem label="Next Review" value={formatDate(client.next_review)} highlight />
              </View>
              {client.pan && (
                <View style={styles.summaryRow}>
                  <SummaryItem label="PAN" value={client.pan} />
                </View>
              )}
            </View>

            {/* Contact Info */}
            {client.contact && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Contact Information</Text>
                <View style={styles.infoCard}>
                  <InfoRow icon={'\u260E'} label="Phone" value={client.contact.phone} />
                  <InfoRow icon={'\u2709'} label="Email" value={client.contact.email} />
                  <InfoRow icon={'\uD83C\uDFE0'} label="Address" value={client.contact.address} />
                </View>
              </View>
            )}

            {/* Holdings */}
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Holdings</Text>
              {(client.holdings || []).length === 0 && (
                <Text style={styles.emptyText}>No holdings data available</Text>
              )}
              {(client.holdings || []).map((h, i) => (
                <View key={i} style={styles.holdingCard}>
                  <View style={styles.holdingTop}>
                    <Text style={styles.holdingName} numberOfLines={1}>{h.name}</Text>
                    <Text
                      style={[
                        styles.holdingReturn,
                        { color: h.return_pct >= 0 ? '#2E7D32' : '#C62828' },
                      ]}
                    >
                      {formatPercent(h.return_pct)}
                    </Text>
                  </View>
                  <View style={styles.holdingBottom}>
                    <Text style={styles.holdingDetail}>
                      Allocation: {h.allocation_pct?.toFixed(1)}%
                    </Text>
                    <Text style={styles.holdingDetail}>
                      Value: {formatINR(h.value_cr)}
                    </Text>
                  </View>
                  {/* Allocation bar */}
                  <View style={styles.allocBar}>
                    <View
                      style={[
                        styles.allocFill,
                        { width: `${Math.min(h.allocation_pct || 0, 100)}%` },
                      ]}
                    />
                  </View>
                </View>
              ))}
            </View>

            <View style={{ height: 30 }} />
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

function SummaryItem({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <View style={styles.summaryItem}>
      <Text style={styles.summaryLabel}>{label}</Text>
      <Text style={[styles.summaryValue, highlight && styles.summaryHighlight]}>{value}</Text>
    </View>
  );
}

function InfoRow({ icon, label, value }: { icon: string; label: string; value?: string }) {
  if (!value) return null;
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoIcon}>{icon}</Text>
      <View style={styles.infoContent}>
        <Text style={styles.infoLabel}>{label}</Text>
        <Text style={styles.infoValue}>{value}</Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: TEAL },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F5F7FA' },
  loadingText: { marginTop: 12, color: '#666', fontSize: 14 },
  body: { flex: 1, backgroundColor: '#F5F7FA' },

  header: {
    backgroundColor: TEAL,
    paddingHorizontal: 20,
    paddingBottom: 14,
    paddingTop: 8,
  },
  backBtn: { marginBottom: 6 },
  backText: { color: MINT, fontSize: 14, fontWeight: '500' },
  headerTitle: { color: '#FFF', fontSize: 22, fontWeight: '800' },

  errorBanner: {
    backgroundColor: '#FFEBEE',
    padding: 14,
    margin: 16,
    borderRadius: 10,
    borderLeftWidth: 4,
    borderLeftColor: '#E53935',
  },
  errorText: { color: '#C62828', fontSize: 13, fontWeight: '500' },
  errorRetry: { color: '#E53935', fontSize: 12, marginTop: 4, fontWeight: '600' },

  summaryCard: {
    backgroundColor: '#FFFFFF',
    margin: 16,
    borderRadius: 14,
    padding: 18,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  summaryRow: { flexDirection: 'row', marginBottom: 14 },
  summaryItem: { flex: 1 },
  summaryLabel: { fontSize: 11, color: '#8E9BAE', fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.5 },
  summaryValue: { fontSize: 16, fontWeight: '700', color: TEAL, marginTop: 4 },
  summaryHighlight: { color: EMERALD },

  section: { paddingHorizontal: 16, marginTop: 8 },
  sectionTitle: { fontSize: 17, fontWeight: '700', color: TEAL, marginBottom: 12 },
  emptyText: { color: '#999', fontSize: 13, fontStyle: 'italic' },

  infoCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 14,
    padding: 16,
    elevation: 2,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.08,
    shadowRadius: 4,
  },
  infoRow: { flexDirection: 'row', alignItems: 'flex-start', marginBottom: 14 },
  infoIcon: { fontSize: 18, marginRight: 12, marginTop: 2 },
  infoContent: { flex: 1 },
  infoLabel: { fontSize: 11, color: '#8E9BAE', fontWeight: '600', textTransform: 'uppercase' },
  infoValue: { fontSize: 14, color: '#1A1A1A', marginTop: 2 },

  holdingCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10,
    elevation: 1,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 3,
  },
  holdingTop: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  holdingName: { fontSize: 15, fontWeight: '600', color: '#1A1A1A', flex: 1, marginRight: 8 },
  holdingReturn: { fontSize: 14, fontWeight: '700' },
  holdingBottom: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 6 },
  holdingDetail: { fontSize: 12, color: '#666' },
  allocBar: {
    height: 4,
    backgroundColor: '#E8ECF0',
    borderRadius: 2,
    marginTop: 10,
    overflow: 'hidden',
  },
  allocFill: {
    height: '100%',
    backgroundColor: EMERALD,
    borderRadius: 2,
  },
});
