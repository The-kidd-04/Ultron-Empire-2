import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface ChatBubbleProps {
  message: string;
  isUser: boolean;
  timestamp?: string;
  toolsUsed?: string[];
}

export default function ChatBubble({ message, isUser, timestamp, toolsUsed }: ChatBubbleProps) {
  return (
    <View style={[styles.row, isUser ? styles.rowUser : styles.rowAI]}>
      <View style={[styles.bubble, isUser ? styles.bubbleUser : styles.bubbleAI]}>
        <Text style={[styles.text, isUser ? styles.textUser : styles.textAI]}>
          {message}
        </Text>
        {toolsUsed && toolsUsed.length > 0 && (
          <View style={styles.toolsRow}>
            {toolsUsed.map((tool, i) => (
              <View key={i} style={styles.toolBadge}>
                <Text style={styles.toolText}>{tool}</Text>
              </View>
            ))}
          </View>
        )}
        {timestamp ? (
          <Text style={[styles.time, isUser ? styles.timeUser : styles.timeAI]}>
            {timestamp}
          </Text>
        ) : null}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: {
    marginVertical: 4,
    paddingHorizontal: 12,
  },
  rowUser: {
    alignItems: 'flex-end',
  },
  rowAI: {
    alignItems: 'flex-start',
  },
  bubble: {
    maxWidth: '80%',
    borderRadius: 16,
    paddingHorizontal: 14,
    paddingVertical: 10,
  },
  bubbleUser: {
    backgroundColor: '#003235',
    borderBottomRightRadius: 4,
  },
  bubbleAI: {
    backgroundColor: '#EAEEF2',
    borderBottomLeftRadius: 4,
  },
  text: {
    fontSize: 15,
    lineHeight: 21,
  },
  textUser: {
    color: '#FFFFFF',
  },
  textAI: {
    color: '#1A1A1A',
  },
  toolsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 6,
    gap: 4,
  },
  toolBadge: {
    backgroundColor: 'rgba(0,140,111,0.15)',
    borderRadius: 8,
    paddingHorizontal: 8,
    paddingVertical: 2,
  },
  toolText: {
    fontSize: 11,
    color: '#008C6F',
    fontWeight: '600',
  },
  time: {
    fontSize: 10,
    marginTop: 4,
  },
  timeUser: {
    color: 'rgba(255,255,255,0.6)',
    textAlign: 'right',
  },
  timeAI: {
    color: '#999',
  },
});
