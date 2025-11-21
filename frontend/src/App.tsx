import { useState, useEffect } from 'react'
import { SessionDashboard } from './components/SessionDashboard'
import { ClipBrowser } from './components/ClipBrowser'
import { MemoryList } from './components/MemoryList'
import { MemorySearch } from './components/MemorySearch'
import { Button } from './components/ui/button'
import { LayoutDashboard, Clock, Brain, Search } from 'lucide-react'

type Tab = 'dashboard' | 'clips' | 'memories' | 'search'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')
  const [isDark, setIsDark] = useState<boolean>(() => {
    const stored = typeof window !== 'undefined' ? localStorage.getItem('crecall-theme') : null
    if (stored) return stored === 'dark'
    // Default dark; if user prefers dark via OS keep dark, if prefers light still default dark per spec
    try {
      const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches
      return prefersDark || true
    } catch {
      return true
    }
  })

  useEffect(() => {
    const root = document.documentElement
    if (isDark) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('crecall-theme', isDark ? 'dark' : 'light')
  }, [isDark])

  useEffect(() => {
    // Listen for OS changes only if user hasn't manually chosen (no stored preference yet)
    const stored = localStorage.getItem('crecall-theme')
    if (stored) return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = (e: MediaQueryListEvent) => {
      setIsDark(e.matches || true) // keep dark default
    }
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold">crecall</h1>
              <p className="text-sm text-muted-foreground">
                Session Recall & Memory Management
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="px-3 py-1 rounded-full bg-green-500/10 text-green-500 text-xs font-medium">
                Connected
              </div>
              <Button
                variant="outline"
                onClick={() => setIsDark(d => !d)}
                className="text-xs"
              >
                {isDark ? 'Light Mode' : 'Dark Mode'}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="border-b">
        <div className="container mx-auto px-4">
          <div className="flex gap-1">
            <TabButton
              active={activeTab === 'dashboard'}
              onClick={() => setActiveTab('dashboard')}
              icon={<LayoutDashboard className="h-4 w-4" />}
            >
              Dashboard
            </TabButton>
            <TabButton
              active={activeTab === 'clips'}
              onClick={() => setActiveTab('clips')}
              icon={<Clock className="h-4 w-4" />}
            >
              Clips
            </TabButton>
            <TabButton
              active={activeTab === 'memories'}
              onClick={() => setActiveTab('memories')}
              icon={<Brain className="h-4 w-4" />}
            >
              Memories
            </TabButton>
            <TabButton
              active={activeTab === 'search'}
              onClick={() => setActiveTab('search')}
              icon={<Search className="h-4 w-4" />}
            >
              Search
            </TabButton>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {activeTab === 'dashboard' && <SessionDashboard />}
        {activeTab === 'clips' && <ClipBrowser />}
        {activeTab === 'memories' && <MemoryList />}
        {activeTab === 'search' && <MemorySearch />}
      </main>
    </div>
  )
}

function TabButton({
  active,
  onClick,
  icon,
  children,
}: {
  active: boolean
  onClick: () => void
  icon: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <Button
      variant={active ? 'default' : 'ghost'}
      onClick={onClick}
      className="rounded-b-none"
    >
      {icon}
      {children}
    </Button>
  )
}

export default App
