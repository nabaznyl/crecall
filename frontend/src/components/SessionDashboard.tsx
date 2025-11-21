import { useQuery } from '@tanstack/react-query'
import { api } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Activity, Clock, FileText, Brain } from 'lucide-react'

export function SessionDashboard() {
  const { data: sessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => api.sessions.list(),
  })

  const { data: clips } = useQuery({
    queryKey: ['clips'],
    queryFn: () => api.clips.list(undefined, 10),
  })

  const { data: memories } = useQuery({
    queryKey: ['memories'],
    queryFn: () => api.memories.list(),
  })

  const activeSession = sessions?.find(s => s.status === 'active')
  const totalSessions = sessions?.length || 0
  const totalClips = clips?.length || 0
  const totalMemories = memories?.length || 0

  return (
    <div className="space-y-4">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Active Session"
          value={activeSession?.session_id || 'None'}
          icon={<Activity className="h-4 w-4 text-muted-foreground" />}
          description={activeSession ? `Started ${new Date(activeSession.created_at).toLocaleDateString()}` : 'No active session'}
        />
        <StatCard
          title="Total Sessions"
          value={totalSessions.toString()}
          icon={<Clock className="h-4 w-4 text-muted-foreground" />}
          description="All time sessions"
        />
        <StatCard
          title="Clips"
          value={totalClips.toString()}
          icon={<FileText className="h-4 w-4 text-muted-foreground" />}
          description="Context snapshots"
        />
        <StatCard
          title="Memories"
          value={totalMemories.toString()}
          icon={<Brain className="h-4 w-4 text-muted-foreground" />}
          description="Saved insights"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Session Timeline</CardTitle>
          <CardDescription>Recent development activity</CardDescription>
        </CardHeader>
        <CardContent>
          {sessionsLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              Loading sessions...
            </div>
          ) : sessions && sessions.length > 0 ? (
            <div className="space-y-4">
              {sessions.slice(0, 5).map((session) => (
                <div
                  key={session.id}
                  className="flex items-center justify-between py-2 border-b last:border-0"
                >
                  <div>
                    <code className="text-sm font-mono">{session.session_id}</code>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(session.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        session.status === 'active'
                          ? 'bg-green-500/10 text-green-500'
                          : 'bg-gray-500/10 text-gray-500'
                      }`}
                    >
                      {session.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              No sessions yet. Start working to create your first session!
            </div>
          )}
        </CardContent>
      </Card>

      {clips && clips.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Recent Clips</CardTitle>
            <CardDescription>Latest context snapshots</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {clips.slice(0, 5).map((clip) => (
                <div
                  key={clip.id}
                  className="flex items-center justify-between py-2 border-b last:border-0"
                >
                  <div className="flex items-center gap-2">
                    <code className="text-sm font-mono text-muted-foreground">
                      {clip.clip_id}
                    </code>
                    {clip.git_branch && (
                      <span className="text-xs text-muted-foreground">
                        on {clip.git_branch}
                      </span>
                    )}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {new Date(clip.created_at).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

function StatCard({
  title,
  value,
  icon,
  description,
}: {
  title: string
  value: string
  icon: React.ReactNode
  description: string
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  )
}
