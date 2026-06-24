import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import TitleBar from './components/TitleBar';
import RenamePage from './pages/RenamePage';
import ExtractExcelPage from './pages/ExtractExcelPage';
import ExtractWordPage from './pages/ExtractWordPage';
import { Login } from './components/Login';
import { usePyWebView } from './hooks/usePyWebView';

type Page = 'rename' | 'extract_excel' | 'extract_word';

export default function App() {
  const { ready, api } = usePyWebView();
  const [page, setPage] = useState<Page>('rename');
  
  const [userEmail, setUserEmail] = useState<string | null>(() => localStorage.getItem('user_email'));
  const [authType, setAuthType] = useState<'company' | 'guest' | null>(() => localStorage.getItem('auth_type') as any);
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Sync session state to python backend on load or when api ready
  useEffect(() => {
    if (ready && api) {
      const email = localStorage.getItem('user_email');
      const type = localStorage.getItem('auth_type');
      if (email && type) {
        if (type === 'guest') {
          api.set_guest_session();
        } else {
          api.set_user_session(email, type);
        }
      }
    }
  }, [ready, api]);

  const handleLoginSuccess = (email: string, role: 'company' | 'guest') => {
    localStorage.setItem('user_email', email);
    localStorage.setItem('auth_type', role);
    setUserEmail(email);
    setAuthType(role);
    setShowLoginModal(false);
  };

  const handleLogout = async () => {
    localStorage.removeItem('user_email');
    localStorage.removeItem('auth_type');
    setUserEmail(null);
    setAuthType(null);
    if (api) {
      await api.set_user_session(null, null);
    }
  };

  const isLoggedIn = !!userEmail;

  return (
    <div className="flex flex-col h-screen w-screen bg-bg overflow-hidden">
      <TitleBar 
        isLoggedIn={isLoggedIn}
        userEmail={userEmail}
        authType={authType}
        onLogout={handleLogout}
        onLoginClick={() => setShowLoginModal(true)}
      />
      <div className="flex flex-1 min-h-0">
        <Sidebar current={page} onNavigate={setPage} />
        <main className="flex-1 min-h-0 overflow-hidden">
          {page === 'rename' && <RenamePage />}
          {page === 'extract_excel' && <ExtractExcelPage />}
          {page === 'extract_word' && <ExtractWordPage />}
        </main>
      </div>

      {/* Show login if not logged in or forced */}
      {(!isLoggedIn || showLoginModal) && (
        <Login 
          api={api}
          onLoginSuccess={handleLoginSuccess}
        />
      )}
    </div>
  );
}
