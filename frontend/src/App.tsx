import { useState } from 'react'
import Sidebar from './components/Sidebar'
import TitleBar from './components/TitleBar'
import RenamePage from './pages/RenamePage'
import ExtractExcelPage from './pages/ExtractExcelPage'
import ExtractWordPage from './pages/ExtractWordPage'

type Page = 'rename' | 'extract_excel' | 'extract_word'

export default function App() {
  const [page, setPage] = useState<Page>('rename')

  return (
    <div className="flex flex-col h-screen w-screen bg-bg overflow-hidden">
      <TitleBar />
      <div className="flex flex-1 min-h-0">
        <Sidebar current={page} onNavigate={setPage} />
        <main className="flex-1 min-h-0 overflow-hidden">
          {page === 'rename' && <RenamePage />}
          {page === 'extract_excel' && <ExtractExcelPage />}
          {page === 'extract_word' && <ExtractWordPage />}
        </main>
      </div>
    </div>
  )
}
