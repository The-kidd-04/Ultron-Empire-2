import React, { useState, useRef, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  KeyboardAvoidingView,
  Platform,
  StyleSheet,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import ChatBubble from '../src/components/ChatBubble';
import VoiceButton from '../src/components/VoiceButton';
import { sendChat } from '../src/services/api';

const TEAL = '#003235';
const EMERALD = '#008C6F';
const MINT = '#63D2B7';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: string;
  toolsUsed?: string[];
}

export default function ChatScreen() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      text: 'Hello! I am Ultron, your AI wealth management assistant. Ask me anything about your portfolio, clients, or market trends.',
      isUser: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    },
  ]);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const flatListRef = useRef<FlatList>(null);

  const addMessage = useCallback((text: string, isUser: boolean, toolsUsed?: string[]) => {
    const msg: Message = {
      id: Date.now().toString() + Math.random().toString(36).slice(2),
      text,
      isUser,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      toolsUsed,
    };
    setMessages((prev) => [...prev, msg]);
    setTimeout(() => flatListRef.current?.scrollToEnd({ animated: true }), 100);
  }, []);

  const handleSend = useCallback(async () => {
    const query = input.trim();
    if (!query || sending) return;

    setInput('');
    addMessage(query, true);
    setSending(true);

    try {
      const result = await sendChat(query);
      addMessage(result.response, false, result.tools_used);
    } catch (err: any) {
      addMessage('Sorry, I could not process your request. Please try again.', false);
    } finally {
      setSending(false);
    }
  }, [input, sending, addMessage]);

  const handleVoiceResponse = useCallback(
    (response: string, toolsUsed: string[]) => {
      addMessage('[Voice message]', true);
      addMessage(response, false, toolsUsed);
    },
    [addMessage]
  );

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Ultron AI</Text>
        <Text style={styles.headerSub}>Wealth Intelligence</Text>
      </View>

      <KeyboardAvoidingView
        style={styles.flex}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        keyboardVerticalOffset={90}
      >
        {/* Messages */}
        <FlatList
          ref={flatListRef}
          data={messages}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <ChatBubble
              message={item.text}
              isUser={item.isUser}
              timestamp={item.timestamp}
              toolsUsed={item.toolsUsed}
            />
          )}
          contentContainerStyle={styles.messageList}
          onContentSizeChange={() => flatListRef.current?.scrollToEnd({ animated: true })}
        />

        {/* Typing indicator */}
        {sending && (
          <View style={styles.typingRow}>
            <ActivityIndicator size="small" color={EMERALD} />
            <Text style={styles.typingText}>Ultron is thinking...</Text>
          </View>
        )}

        {/* Input Bar */}
        <View style={styles.inputBar}>
          <VoiceButton onTranscription={handleVoiceResponse} disabled={sending} />
          <TextInput
            style={styles.input}
            placeholder="Ask Ultron..."
            placeholderTextColor="#999"
            value={input}
            onChangeText={setInput}
            multiline
            maxLength={1000}
            editable={!sending}
            onSubmitEditing={handleSend}
            blurOnSubmit={false}
          />
          <TouchableOpacity
            style={[styles.sendBtn, (!input.trim() || sending) && styles.sendBtnDisabled]}
            onPress={handleSend}
            disabled={!input.trim() || sending}
          >
            <Text style={styles.sendIcon}>{'\u27A4'}</Text>
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: TEAL },
  flex: { flex: 1, backgroundColor: '#F5F7FA' },

  header: {
    backgroundColor: TEAL,
    paddingHorizontal: 20,
    paddingBottom: 14,
    paddingTop: 8,
  },
  headerTitle: { color: '#FFF', fontSize: 20, fontWeight: '800' },
  headerSub: { color: MINT, fontSize: 12, fontWeight: '500', marginTop: 2 },

  messageList: {
    paddingVertical: 16,
  },

  typingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 8,
    gap: 8,
  },
  typingText: { color: '#666', fontSize: 13, fontStyle: 'italic' },

  inputBar: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    paddingHorizontal: 10,
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E8ECF0',
    gap: 8,
  },
  input: {
    flex: 1,
    backgroundColor: '#F5F7FA',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    fontSize: 15,
    maxHeight: 100,
    color: '#1A1A1A',
  },
  sendBtn: {
    backgroundColor: EMERALD,
    width: 44,
    height: 44,
    borderRadius: 22,
    justifyContent: 'center',
    alignItems: 'center',
  },
  sendBtnDisabled: {
    backgroundColor: '#CCC',
  },
  sendIcon: {
    color: '#FFF',
    fontSize: 18,
  },
});
