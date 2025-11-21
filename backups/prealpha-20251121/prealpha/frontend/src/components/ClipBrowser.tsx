import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api, type Clip } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Clock, GitBranch, Folder, Search } from 'lucide-react'

export function ClipBrowser() {
  const [sessionFilter, setSessionFilter] = useState<string>('')
  const [searchTerm, setSearchTerm] = useState<string>('')

  const { data: clips, isLoading, error, refetch } = useQuery({
    queryKey: ['clips', sessionFilter],
    queryFn: () => api.clips.list(sessionFilter || undefined, 50),
  })

  const filteredClips = clips?.filter(clip => {
    if (!searchTerm) return true
    const searchLower = searchTerm.toLowerCase()
    return (
      clip.clip_id.toLowerCase().includes(searchLower) ||
      clip.name?.toLowerCase().includes(searchLower) ||
      clip.git_branch?.toLowerCase().includes(searchLower)
    )
  })

  const handlePrune = async () => {
    if (confirm('Are you sure you want to prune old clips? This will keep only the last 100.')) {
      try {
        await api.clips.prune(100)
        refetch()
      } catch (err) {
        console.error('Failed to prune clips:', err)
      }
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Clip Browser
            </span>
            <Button variant="outline" size="sm" onClick={handlePrune}>
              Prune Old Clips
            </Button>
          </CardTitle>
          <CardDescription>
            Browse and search through captured development clips
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Search and Filter */}
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search clips..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Input
                placeholder="Filter by session ID..."
                value={sessionFilter}
                onChange={(e) => setSessionFilter(e.target.value)}
                className="w-64"
              />
            </div>

            {/* Clips List */}
            {isLoading && (
              <div className="text-center py-8 text-muted-foreground">
                Loading clips...
              </div>
            )}

            {error && (
              <div className="text-center py-8 text-destructive">
                Error loading clips: {error.message}
              </div>
            )}

            {filteredClips && filteredClips.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No clips found
              </div>
            )}

            <div className="space-y-2">
              {filteredClips?.map((clip) => (
                <ClipItem key={clip.id} clip={clip} />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function ClipItem({ clip }: { clip: Clip }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <Card className="hover:bg-accent/50 transition-colors cursor-pointer">
      <CardContent className="p-4" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 space-y-1">
            <div className="flex items-center gap-2">
              <code className="text-sm font-mono text-muted-foreground">
                {clip.clip_id}
              </code>
              {clip.is_auto && (
                <Badge variant="secondary" className="text-xs">
                  Auto
                </Badge>
              )}
              {clip.name && (
                <Badge variant="outline" className="text-xs">
                  {clip.name}
                </Badge>
              )}
            </div>

            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {new Date(clip.created_at).toLocaleString()}
              </span>
              {clip.git_branch && (
                <span className="flex items-center gap-1">
                  <GitBranch className="h-3 w-3" />
                  {clip.git_branch}
                </span>
              )}
              {clip.working_directory && (
                <span className="flex items-center gap-1">
                  <Folder className="h-3 w-3" />
                  {clip.working_directory}
                </span>
              )}
            </div>
          </div>
        </div>

        {expanded && (
          <div className="mt-4 pt-4 border-t">
            <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto">
              {JSON.stringify(clip.content, null, 2)}
            </pre>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
