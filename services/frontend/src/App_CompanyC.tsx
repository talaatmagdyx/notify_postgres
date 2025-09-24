import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import './App.css';

// Company C Configuration
const COMPANY_CONFIG = {
  companyCode: 'COMP_C',
  companyName: 'Company Gamma',
  backendUrl: 'http://localhost:5003',
  primaryColor: '#4267B2', // Facebook blue for Company C
  secondaryColor: '#365899'
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

  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io(COMPANY_CONFIG.backendUrl);
    setSocket(newSocket);

    // Listen for real-time updates
    newSocket.on('new_engagement', (data: any) => {
      console.log('New engagement:', data);
      addNotification({
        id: Date.now(),
        type: 'new_engagement',
        message: `New ${data.channel} engagement from ${data.user_identifier}`,
        timestamp: new Date().toISOString()
      });
      fetchEngagements(); // Refresh the list
    });

    newSocket.on('status_update', (data: any) => {
      console.log('Status update:', data);
      addNotification({
        id: Date.now(),
        type: 'status_update',
        message: `Status updated to ${data.new_status}`,
        timestamp: new Date().toISOString()
      });
      fetchEngagements(); // Refresh the list
    });

    // Load initial data
    fetchEngagements();
    fetchCompanyInfo();

    return () => {
      newSocket.disconnect();
    };
  }, []);

  const fetchEngagements = async () => {
    try {
      const response = await fetch(`${COMPANY_CONFIG.backendUrl}/api/engagements`);
      const data = await response.json();
      setEngagements(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching engagements:', error);
      setLoading(false);
    }
  };

  const fetchCompanyInfo = async () => {
    try {
      const response = await fetch(`${COMPANY_CONFIG.backendUrl}/api/company/info`);
      const data = await response.json();
      setCompanyInfo(data);
    } catch (error) {
      console.error('Error fetching company info:', error);
    }
  };

  const updateEngagementStatus = async (id: number, newStatus: string) => {
    try {
      await fetch(`${COMPANY_CONFIG.backendUrl}/api/engagements/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });
      fetchEngagements(); // Refresh the list
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

  if (loading) {
    return (
      <div className="app" style={{ backgroundColor: COMPANY_CONFIG.secondaryColor }}>
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading {COMPANY_CONFIG.companyName} engagements...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app" style={{ backgroundColor: COMPANY_CONFIG.secondaryColor }}>
      {/* Header */}
      <div className="header" style={{ backgroundColor: COMPANY_CONFIG.primaryColor }}>
        <div className="header-content">
          <h1>🏢 {COMPANY_CONFIG.companyName}</h1>
          <div className="company-info">
            {companyInfo && (
              <span>Schema: {companyInfo.schema_name} | Port: {companyInfo.backend_port}</span>
            )}
          </div>
        </div>
      </div>

      {/* Notification Bar */}
      {notifications.length > 0 && (
        <div className="notification-bar">
          {notifications.map(notification => (
            <div key={notification.id} className={`notification ${notification.type}`}>
              <span>{notification.message}</span>
              <button onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}>
                ×
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        <div className="sidebar">
          <div className="sidebar-header">
            <h3>📊 Analytics</h3>
          </div>
          <div className="stats">
            <div className="stat">
              <span className="stat-number">{engagements.length}</span>
              <span className="stat-label">Total Engagements</span>
            </div>
            <div className="stat">
              <span className="stat-number">
                {engagements.filter(e => e.status === 'new').length}
              </span>
              <span className="stat-label">New</span>
            </div>
            <div className="stat">
              <span className="stat-number">
                {engagements.filter(e => e.status === 'in_progress').length}
              </span>
              <span className="stat-label">In Progress</span>
            </div>
          </div>
        </div>

        <div className="engagements-list">
          <div className="list-header">
            <h2>💬 Recent Engagements</h2>
            <button onClick={fetchEngagements} className="refresh-btn">🔄 Refresh</button>
          </div>
          
          {engagements.length === 0 ? (
            <div className="empty-state">
              <p>No engagements found</p>
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
                      </div>
                    </div>
                    <div className="engagement-meta">
                      <span 
                        className="status-badge" 
                        style={{ backgroundColor: getStatusColor(engagement.status) }}
                      >
                        {engagement.status}
                      </span>
                      <span className="timestamp">
                        {new Date(engagement.created_at).toLocaleString()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="engagement-actions">
                    <button 
                      onClick={() => updateEngagementStatus(engagement.id, 'in_progress')}
                      className="action-btn primary"
                    >
                      Start
                    </button>
                    <button 
                      onClick={() => updateEngagementStatus(engagement.id, 'resolved')}
                      className="action-btn success"
                    >
                      Resolve
                    </button>
                    <button 
                      onClick={() => updateEngagementStatus(engagement.id, 'closed')}
                      className="action-btn secondary"
                    >
                      Close
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
