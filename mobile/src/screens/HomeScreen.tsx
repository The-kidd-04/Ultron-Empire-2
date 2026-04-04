import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, StyleSheet } from 'react-native';

const API_URL = 'https://api.ultron.pmssahihai.com/api/v1';

export default function HomeScreen() {
  const [dashboard, setDashboard] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_URL}/dashboard`).then(r => r.json()).then(setDashboard).catch(() => {});
  }, []);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.logo}>Ultron Empire</Text>
        <Text style={styles.subtitle}>PMS Sahi Hai</Text>
      </View>

      <View style={styles.cardRow}>
        <StatCard title="Total AUM" value={dashboard ? `₹${dashboard.aum?.total_cr} Cr` : '—'} />
        <StatCard title="Clients" value={dashboard?.aum?.client_count || '—'} />
      </View>
      <View style={styles.cardRow}>
        <StatCard title="🔴 Critical" value={dashboard?.alerts?.critical || 0} color="#FF0000" />
        <StatCard title="🟡 Important" value={dashboard?.alerts?.important || 0} color="#FFB800" />
      </View>

      <TouchableOpacity style={styles.voiceButton}>
        <Text style={styles.voiceText}>🎤 Ask Ultron</Text>
      </TouchableOpacity>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Alerts</Text>
        {(dashboard?.alerts?.recent || []).map((a: any, i: number) => (
          <View key={i} style={styles.alertItem}>
            <Text style={styles.alertTitle}>{a.priority === 'critical' ? '🔴' : '🔵'} {a.title}</Text>
          </View>
        ))}
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Overdue Reviews</Text>
        {(dashboard?.reviews?.overdue_clients || []).map((c: any, i: number) => (
          <View key={i} style={styles.alertItem}>
            <Text>{c.name} — due {c.due}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

function StatCard({ title, value, color }: { title: string; value: any; color?: string }) {
  return (
    <View style={[styles.card, color ? { borderLeftColor: color } : {}]}>
      <Text style={styles.cardLabel}>{title}</Text>
      <Text style={styles.cardValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F5F7FA' },
  header: { backgroundColor: '#003235', padding: 20, paddingTop: 50 },
  logo: { color: 'white', fontSize: 22, fontWeight: 'bold' },
  subtitle: { color: '#63D2B7', fontSize: 12, marginTop: 2 },
  cardRow: { flexDirection: 'row', padding: 10, gap: 10 },
  card: { flex: 1, backgroundColor: 'white', borderRadius: 10, padding: 15, borderLeftWidth: 4, borderLeftColor: '#008C6F' },
  cardLabel: { fontSize: 12, color: '#999' },
  cardValue: { fontSize: 22, fontWeight: 'bold', color: '#003235', marginTop: 4 },
  voiceButton: { backgroundColor: '#008C6F', margin: 15, padding: 18, borderRadius: 12, alignItems: 'center' },
  voiceText: { color: 'white', fontSize: 16, fontWeight: 'bold' },
  section: { padding: 15 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#003235', marginBottom: 10 },
  alertItem: { backgroundColor: 'white', padding: 12, borderRadius: 8, marginBottom: 8 },
  alertTitle: { fontSize: 14 },
});
