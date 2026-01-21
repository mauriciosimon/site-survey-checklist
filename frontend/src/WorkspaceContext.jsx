import { createContext, useContext, useState, useEffect } from 'react';
import { workspaceApi } from './api';
import { useAuth } from './AuthContext';

const WorkspaceContext = createContext(null);

export function WorkspaceProvider({ children }) {
  const { user } = useAuth();
  const [workspaces, setWorkspaces] = useState([]);
  const [currentWorkspace, setCurrentWorkspace] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load workspaces when user is authenticated
  useEffect(() => {
    if (user) {
      loadWorkspaces();
    } else {
      setWorkspaces([]);
      setCurrentWorkspace(null);
      setLoading(false);
    }
  }, [user]);

  const loadWorkspaces = async () => {
    try {
      setLoading(true);
      const response = await workspaceApi.getAll({ is_active: true });
      const workspaceList = response.data;
      setWorkspaces(workspaceList);

      // Restore selected workspace from localStorage or default to first
      const savedWorkspaceId = localStorage.getItem('currentWorkspaceId');
      if (savedWorkspaceId) {
        const savedWorkspace = workspaceList.find(w => w.id === parseInt(savedWorkspaceId));
        if (savedWorkspace) {
          setCurrentWorkspace(savedWorkspace);
        } else if (workspaceList.length > 0) {
          setCurrentWorkspace(workspaceList[0]);
        }
      } else if (workspaceList.length > 0) {
        setCurrentWorkspace(workspaceList[0]);
      }
    } catch (error) {
      console.error('Failed to load workspaces:', error);
    } finally {
      setLoading(false);
    }
  };

  const switchWorkspace = (workspace) => {
    setCurrentWorkspace(workspace);
    localStorage.setItem('currentWorkspaceId', workspace.id.toString());
  };

  const value = {
    workspaces,
    currentWorkspace,
    switchWorkspace,
    loading,
    refreshWorkspaces: loadWorkspaces,
  };

  return (
    <WorkspaceContext.Provider value={value}>
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within a WorkspaceProvider');
  }
  return context;
}
