import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

interface Engagement {
  id: number;
  channel: string;
  user_identifier: string;
  status: string;
  created_at: string;
  text: string;
  engagement_id: string;
}

interface Notification {
  type: 'interaction_change' | 'status_change';
  data: any;
  timestamp: Date;
}

const App: React.FC = () => {
  const [engagements, setEngagements] = useState<Engagement[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [socket, setSocket] = useState<any>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [newMessage, setNewMessage] = useState('');
  const [selectedChannel, setSelectedChannel] = useState('whatsapp');

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io('http://localhost:5001');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setIsConnected(false);
    });

    newSocket.on('interaction_change', (data: any) => {
      console.log('Interaction change:', data);
      addNotification('interaction_change', data);
      
      // Refresh engagements list
      fetchEngagements();
    });

    newSocket.on('status_change', (data: any) => {
      console.log('Status change:', data);
      addNotification('status_change', data);
      
      // Update engagement in list
      setEngagements(prev => 
        prev.map(engagement => 
          engagement.id === data.interaction_id 
            ? { ...engagement, status: data.new_status }
            : engagement
        )
      );
    });

    // Fetch initial engagements
    fetchEngagements();

    return () => {
      newSocket.close();
    };
  }, []);

  const fetchEngagements = async () => {
    try {
      const response = await fetch('http://localhost:5001/api/engagements');
      const data = await response.json();
      setEngagements(data);
    } catch (error) {
      console.error('Error fetching engagements:', error);
    }
  };

  const addNotification = (type: 'interaction_change' | 'status_change', data: any) => {
    const notification: Notification = {
      type,
      data,
      timestamp: new Date()
    };
    
    setNotifications(prev => [notification, ...prev.slice(0, 9)]); // Keep last 10 notifications
  };

  const createEngagement = async () => {
    if (!newMessage.trim()) return;

    try {
      const response = await fetch('http://localhost:5001/api/engagements', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          channel: selectedChannel,
          user_identifier: '+1234567890',
          text: newMessage,
          frontend_json: {
            message_type: 'text',
            sender_name: 'Test User'
          }
        }),
      });

      if (response.ok) {
        setNewMessage('');
        fetchEngagements();
      }
    } catch (error) {
      console.error('Error creating engagement:', error);
    }
  };

  const updateStatus = async (id: number, status: string) => {
    try {
      const response = await fetch(`http://localhost:5001/api/engagements/${id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });

      if (response.ok) {
        fetchEngagements();
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return '#4CAF50';
      case 'in_progress': return '#FF9800';
      case 'resolved': return '#2196F3';
      case 'closed': return '#9E9E9E';
      default: return '#666';
    }
  };

  const getChannelIcon = (channel: string) => {
    switch (channel) {
      case 'whatsapp': return '📱';
      case 'twitter': return '🐦';
      case 'facebook': return '📘';
      case 'email': return '📧';
      default: return '💬';
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <h1>📱 Engagement Dashboard</h1>
        <div className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </div>

      <div className="main-content">
        {/* Left Sidebar - Engagements List */}
        <div className="sidebar">
          <h2>Recent Engagements</h2>
          <div className="engagements-list">
            {engagements.map((engagement) => (
              <div key={engagement.id} className="engagement-item">
                <div className="engagement-header">
                  <span className="channel-icon">
                    {getChannelIcon(engagement.channel)}
                  </span>
                  <span className="user">{engagement.user_identifier}</span>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(engagement.status) }}
                  >
                    {engagement.status}
                  </span>
                </div>
                <div className="engagement-text">{engagement.text}</div>
                <div className="engagement-time">
                  {new Date(engagement.created_at).toLocaleString()}
                </div>
                <div className="engagement-actions">
                  <button 
                    onClick={() => updateStatus(engagement.id, 'in_progress')}
                    className="btn btn-orange"
                  >
                    In Progress
                  </button>
                  <button 
                    onClick={() => updateStatus(engagement.id, 'resolved')}
                    className="btn btn-blue"
                  >
                    Resolve
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Sidebar - Notifications */}
        <div className="notifications-sidebar">
          <h2>🔔 Live Notifications</h2>
          <div className="notifications-list">
            {notifications.map((notification, index) => (
              <div key={index} className="notification-item">
                <div className="notification-header">
                  <span className="notification-type">
                    {notification.type === 'interaction_change' ? '🔔' : '📊'}
                  </span>
                  <span className="notification-time">
                    {notification.timestamp.toLocaleTimeString()}
                  </span>
                </div>
                <div className="notification-content">
                  {notification.type === 'interaction_change' ? (
                    <div>
                      <strong>{notification.data.operation}</strong> - {notification.data.channel}
                      <br />
                      User: {notification.data.user_identifier}
                      <br />
                      Text: {notification.data.text?.substring(0, 50)}...
                    </div>
                  ) : (
                    <div>
                      Status Change: <strong>{notification.data.old_status}</strong> → <strong>{notification.data.new_status}</strong>
                      <br />
                      ID: {notification.data.interaction_id}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Input */}
      <div className="input-section">
        <div className="input-group">
          <select 
            value={selectedChannel} 
            onChange={(e) => setSelectedChannel(e.target.value)}
            className="channel-select"
          >
            <option value="whatsapp">📱 WhatsApp</option>
            <option value="twitter">🐦 Twitter</option>
            <option value="facebook">📘 Facebook</option>
            <option value="email">📧 Email</option>
          </select>
          <input
            type="text"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            placeholder="Type a message..."
            className="message-input"
            onKeyPress={(e) => e.key === 'Enter' && createEngagement()}
          />
          <button onClick={createEngagement} className="send-btn">
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;