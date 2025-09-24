import React, { useState, useEffect, useCallback } from 'react';
import io from 'socket.io-client';
import './App.css';

// Company configurations
const COMPANY_CONFIGS = {
  'comp_a': {
    companyCode: 'COMP_A',
    companyName: 'Company Alpha',
    backendUrl: 'http://localhost:5001',
    primaryColor: '#25D366', // WhatsApp green
    secondaryColor: '#128C7E',
    channels: ['whatsapp', 'email']
  },
  'comp_b': {
    companyCode: 'COMP_B',
    companyName: 'Company Beta',
    backendUrl: 'http://localhost:5002',
    primaryColor: '#1DA1F2', // Twitter blue
    secondaryColor: '#0D8BD9',
    channels: ['twitter', 'facebook']
  },
  'comp_c': {
    companyCode: 'COMP_C',
    companyName: 'Company Gamma',
    backendUrl: 'http://localhost:5003',
    primaryColor: '#4267B2', // Facebook blue
    secondaryColor: '#365899',
    channels: ['whatsapp', 'twitter', 'facebook', 'email']
  }
};

interface Engagement {
  id: number;
  channel: string;
  user_identifier: string;
  status: string;
  text: string;
  created_at: string;
  updated_at: string;
  frontend_json: any;
}

interface Notification {
  id: number;
  type: 'new_engagement' | 'status_update';
  message: string;
  timestamp: string;
}

function App() {
  const [engagements, setEngagements] = useState<Engagement[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [socket, setSocket] = useState<any>(null);
  const [companyInfo, setCompanyInfo] = useState<any>(null);
  const [currentCompany, setCurrentCompany] = useState<string>('comp_a');
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected');
  const [newEngagementCount, setNewEngagementCount] = useState(0);

  // Get current company configuration
  const companyConfig = COMPANY_CONFIGS[currentCompany as keyof typeof COMPANY_CONFIGS];

  const fetchEngagements = useCallback(async () => {
    try {
      const response = await fetch(`${companyConfig.backendUrl}/api/engagements`);
      const data = await response.json();
      setEngagements(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching engagements:', error);
      setLoading(false);
    }
  }, [companyConfig.backendUrl]);

  const fetchCompanyInfo = useCallback(async () => {
    try {
      const response = await fetch(`${companyConfig.backendUrl}/api/company/info`);
      const data = await response.json();
      setCompanyInfo(data);
    } catch (error) {
      console.error('Error fetching company info:', error);
    }
  }, [companyConfig.backendUrl]);

  useEffect(() => {
    // Connect to WebSocket for current company
    if (socket) {
      socket.disconnect();
    }

    setConnectionStatus('connecting');
    const newSocket = io(companyConfig.backendUrl, {
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true
    });
    setSocket(newSocket);

    // Connection event handlers
    newSocket.on('connect', () => {
      console.log('🔌 Connected to WebSocket');
      setConnectionStatus('connected');
      newSocket.emit('join_company', { company: companyConfig.companyCode });
    });

    newSocket.on('disconnect', () => {
      console.log('🔌 Disconnected from WebSocket');
      setConnectionStatus('disconnected');
    });

    newSocket.on('connect_error', (error: any) => {
      console.error('❌ WebSocket connection error:', error);
      setConnectionStatus('disconnected');
    });

    // Listen for real-time updates
    newSocket.on('new_engagement', (data: any) => {
      console.log('New engagement:', data);
      
      // Add notification
      addNotification({
        id: Date.now(),
        type: 'new_engagement',
        message: `New ${data.channel} engagement from ${data.user_identifier}`,
        timestamp: new Date().toISOString()
      });
      
      // Add engagement to the list in real-time (no refresh needed)
      const newEngagement: Engagement = {
        id: data.id,
        channel: data.channel,
        user_identifier: data.user_identifier,
        status: data.status,
        text: data.text || 'New engagement',
        created_at: data.created_at || new Date().toISOString(),
        updated_at: data.updated_at || new Date().toISOString(),
        frontend_json: data.frontend_json || {}
      };
      
      setEngagements(prev => {
        // Check if engagement already exists to avoid duplicates
        const exists = prev.some(eng => eng.id === newEngagement.id);
        if (exists) {
          console.log('Engagement already exists, skipping duplicate');
          return prev;
        }
        console.log('Adding new engagement to list:', newEngagement);
        setNewEngagementCount(prev => prev + 1);
        return [newEngagement, ...prev];
      });
    });

    newSocket.on('status_update', (data: any) => {
      console.log('Status update:', data);
      
      // Add notification
      addNotification({
        id: Date.now(),
        type: 'status_update',
        message: `Status updated to ${data.new_status}`,
        timestamp: new Date().toISOString()
      });
      
      // Update engagement status in real-time (no refresh needed)
      setEngagements(prev => 
        prev.map(engagement => 
          engagement.id === data.id 
            ? { ...engagement, status: data.new_status, updated_at: new Date().toISOString() }
            : engagement
        )
      );
    });

    // Load initial data
    fetchEngagements();
    fetchCompanyInfo();

    return () => {
      newSocket.disconnect();
    };
  }, [currentCompany, companyConfig.backendUrl, fetchEngagements, fetchCompanyInfo]);

  const updateEngagementStatus = async (id: number, newStatus: string) => {
    try {
      await fetch(`${companyConfig.backendUrl}/api/engagements/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });
      // No need to refresh - WebSocket will handle the update
    } catch (error) {
      console.error('Error updating engagement:', error);
    }
  };

  const addNotification = (notification: Notification) => {
    setNotifications(prev => [notification, ...prev.slice(0, 4)]); // Keep only last 5
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
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

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return '#FF6B6B';
      case 'in_progress': return '#4ECDC4';
      case 'resolved': return '#45B7D1';
      case 'closed': return '#96CEB4';
      case 'escalated': return '#FFEAA7';
      default: return '#DDA0DD';
    }
  };

  const switchCompany = (companyKey: string) => {
    setCurrentCompany(companyKey);
    setLoading(true);
    setEngagements([]);
    setNotifications([]);
  };

  if (loading) {
    return (
      <div className="app" style={{ backgroundColor: companyConfig.secondaryColor }}>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading {companyConfig.companyName} engagements...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app" style={{ backgroundColor: companyConfig.secondaryColor }}>
      {/* Header */}
      <div className="header" style={{ backgroundColor: companyConfig.primaryColor }}>
        <div className="header-content">
          <div className="header-left">
            <h1>🏢 {companyConfig.companyName}</h1>
            <div className="company-info">
              {companyInfo && (
                <span>Schema: {companyInfo.schema_name} | Port: {companyInfo.backend_port}</span>
              )}
            </div>
          </div>
          <div className="header-right">
            <div className="connection-status">
              <span className={`status-indicator ${connectionStatus}`}>
                {connectionStatus === 'connected' ? '🟢' : 
                 connectionStatus === 'connecting' ? '🟡' : '🔴'}
              </span>
              <span className="status-text">
                {connectionStatus === 'connected' ? 'Connected' : 
                 connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
              </span>
            </div>
            <div className="notification-indicator">
              {notifications.length > 0 && (
                <span className="notification-count">{notifications.length}</span>
              )}
              🔔
            </div>
          </div>
        </div>
      </div>

      {/* Company Switcher */}
      <div className="company-switcher">
        <h3>Switch Company:</h3>
        <div className="company-buttons">
          {Object.entries(COMPANY_CONFIGS).map(([key, config]) => (
            <button
              key={key}
              className={`company-btn ${currentCompany === key ? 'active' : ''}`}
              onClick={() => switchCompany(key)}
              style={{
                backgroundColor: currentCompany === key ? config.primaryColor : '#f0f0f0',
                color: currentCompany === key ? 'white' : 'black'
              }}
            >
              {config.companyName}
            </button>
          ))}
        </div>
      </div>


      {/* Main Content */}
      <div className="main-content">
        <div className="sidebar">
          <div className="sidebar-header">
            <h3>📊 Analytics Dashboard</h3>
          </div>
          
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📈</div>
              <div className="stat-content">
                <span className="stat-number">{engagements.length}</span>
                <span className="stat-label">Total Engagements</span>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🆕</div>
              <div className="stat-content">
                <span className="stat-number">{engagements.filter(e => e.status === 'new').length}</span>
                <span className="stat-label">New</span>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">⚡</div>
              <div className="stat-content">
                <span className="stat-number">{engagements.filter(e => e.status === 'in_progress').length}</span>
                <span className="stat-label">In Progress</span>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">✅</div>
              <div className="stat-content">
                <span className="stat-number">{engagements.filter(e => e.status === 'resolved').length}</span>
                <span className="stat-label">Resolved</span>
              </div>
            </div>
          </div>
          
          <div className="channel-stats">
            <h4>📱 Channel Breakdown</h4>
            {companyConfig.channels.map(channel => (
              <div key={channel} className="channel-stat">
                <div className="channel-info">
                  <span className="channel-icon">{getChannelIcon(channel)}</span>
                  <span className="channel-name">{channel}</span>
                </div>
                <div className="channel-count">
                  <span className="count-number">{engagements.filter(e => e.channel === channel).length}</span>
                  <div className="count-bar">
                    <div 
                      className="count-fill" 
                      style={{ 
                        width: `${(engagements.filter(e => e.channel === channel).length / engagements.length) * 100}%`,
                        backgroundColor: companyConfig.primaryColor
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Recent Notifications Section */}
          <div className="recent-notifications">
            <div className="notifications-header">
              <div className="notifications-title">
                <div className="notification-icon">🔔</div>
                <h4>Recent Notifications</h4>
                {notifications.length > 0 && (
                  <span className="notification-badge">{notifications.length}</span>
                )}
              </div>
              <button 
                className="clear-notifications-btn"
                onClick={() => setNotifications([])}
                disabled={notifications.length === 0}
              >
                Clear All
              </button>
            </div>
            
            {notifications.length === 0 ? (
              <div className="no-notifications">
                <div className="no-notifications-icon">🔕</div>
                <p>No recent notifications</p>
                <small>New engagements and updates will appear here</small>
              </div>
            ) : (
              <div className="notifications-list-sidebar">
                {notifications.slice(0, 5).map(notification => (
                  <div key={notification.id} className={`notification-item ${notification.type}`}>
                    <div className="notification-icon-wrapper">
                      <div className={`notification-type-icon ${notification.type}`}>
                        {notification.type === 'new_engagement' ? '📩' : '🔄'}
                      </div>
                    </div>
                    <div className="notification-content">
                      <div className="notification-message">{notification.message}</div>
                      <div className="notification-time">
                        {new Date(notification.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                    <button 
                      className="notification-remove"
                      onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="engagements-list">
          <div className="list-header">
            <h2>💬 Recent Engagements</h2>
            <div className="list-actions">
              <button onClick={fetchEngagements} className="refresh-btn">
                🔄 Refresh
              </button>
              <div className="engagement-count">
                {engagements.length} engagements
                {newEngagementCount > 0 && (
                  <span className="new-count">+{newEngagementCount} new</span>
                )}
              </div>
            </div>
          </div>
          
          {engagements.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📭</div>
              <h3>No engagements found</h3>
              <p>Generate some test data to see engagements here</p>
            </div>
          ) : (
            <div className="engagements">
              {engagements.map(engagement => (
                <div key={engagement.id} className="engagement-card">
                  <div className="engagement-header">
                    <div className="engagement-info">
                      <span className="channel-icon">{getChannelIcon(engagement.channel)}</span>
                      <div className="engagement-details">
                        <h4>{engagement.user_identifier}</h4>
                        <p className="engagement-text">{engagement.text}</p>
                        <div className="engagement-meta-small">
                          <span className="engagement-id">ID: {engagement.id}</span>
                          <span className="engagement-time">
                            {new Date(engagement.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="engagement-status">
                      <span 
                        className="status-badge" 
                        style={{ backgroundColor: getStatusColor(engagement.status) }}
                      >
                        {engagement.status.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  
                  <div className="engagement-actions">
                    <button 
                      onClick={() => updateEngagementStatus(engagement.id, 'in_progress')}
                      className="action-btn primary"
                      disabled={engagement.status === 'in_progress'}
                    >
                      ▶️ Start
                    </button>
                    <button 
                      onClick={() => updateEngagementStatus(engagement.id, 'resolved')}
                      className="action-btn success"
                      disabled={engagement.status === 'resolved'}
                    >
                      ✅ Resolve
                    </button>
                    <button 
                      onClick={() => updateEngagementStatus(engagement.id, 'closed')}
                      className="action-btn secondary"
                      disabled={engagement.status === 'closed'}
                    >
                      🔒 Close
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;