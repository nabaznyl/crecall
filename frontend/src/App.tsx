import { useState } from 'react'
import { SessionDashboard } from './components/SessionDashboard'
import { ClipBrowser } from './components/ClipBrowser'
import { MemoryList } from './components/MemoryList'
import { MemorySearch } from './components/MemorySearch'
import { Button } from './components/ui/button'
import { LayoutDashboard, Clock, Brain, Search } from 'lucide-react'

type Tab = 'dashboard' | 'clips' | 'memories' | 'search'

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')

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
