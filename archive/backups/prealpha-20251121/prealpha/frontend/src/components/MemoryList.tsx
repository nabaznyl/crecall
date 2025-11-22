import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, type Memory, type MemoryCreate } from '@/services/api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Brain, Plus, Search, Tag, Trash2 } from 'lucide-react'

export function MemoryList() {
  const [searchTerm, setSearchTerm] = useState<string>('')
  const [showAddForm, setShowAddForm] = useState(false)
  const queryClient = useQueryClient()

  const { data: memories, isLoading, error } = useQuery({
    queryKey: ['memories'],
    queryFn: () => api.memories.list(),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.memories.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['memories'] })
    },
  })

  const filteredMemories = memories?.filter(memory => {
    if (!searchTerm) return true
    const searchLower = searchTerm.toLowerCase()
    return (
      memory.content.toLowerCase().includes(searchLower) ||
      memory.tags?.some(tag => tag.toLowerCase().includes(searchLower)) ||
      memory.category?.toLowerCase().includes(searchLower)
    )
  })

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this memory?')) {
      deleteMutation.mutate(id)
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Memory System
            </span>
            <Button
              variant="default"
              size="sm"
              onClick={() => setShowAddForm(!showAddForm)}
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Memory
            </Button>
          </CardTitle>
          <CardDescription>
            Your flagship feature - never lose context again!
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Add Memory Form */}
            {showAddForm && (
              <AddMemoryForm
                onSuccess={() => {
                  setShowAddForm(false)
                  queryClient.invalidateQueries({ queryKey: ['memories'] })
                }}
                onCancel={() => setShowAddForm(false)}
              />
            )}

            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search memories by content, tags, or category..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-9"
              />
            </div>

            {/* Memories List */}
            {isLoading && (
              <div className="text-center py-8 text-muted-foreground">
                Loading memories...
              </div>
            )}

            {error && (
              <div className="text-center py-8 text-destructive">
                Error loading memories: {error.message}
              </div>
            )}

            {filteredMemories && filteredMemories.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No memories found. Add your first memory to get started!
              </div>
            )}

            <div className="space-y-2">
              {filteredMemories?.map((memory) => (
                <MemoryItem
                  key={memory.id}
                  memory={memory}
                  onDelete={() => handleDelete(memory.id)}
                />
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

function MemoryItem({ memory, onDelete }: { memory: Memory; onDelete: () => void }) {
  const importanceColor = {
    critical: 'destructive',
    high: 'default',
    medium: 'secondary',
    low: 'outline',
  }[memory.importance || 'medium'] as 'destructive' | 'default' | 'secondary' | 'outline'

  return (
    <Card className="hover:bg-accent/50 transition-colors">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 space-y-2">
            <p className="text-sm">{memory.content}</p>

            <div className="flex items-center gap-2 flex-wrap">
              {memory.category && (
                <Badge variant="outline" className="text-xs">
                  {memory.category}
                </Badge>
              )}
              {memory.importance && (
                <Badge variant={importanceColor} className="text-xs">
                  {memory.importance}
                </Badge>
              )}
              {memory.tags?.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs flex items-center gap-1">
                  <Tag className="h-3 w-3" />
                  {tag}
                </Badge>
              ))}
            </div>

            <div className="text-xs text-muted-foreground">
              {new Date(memory.created_at).toLocaleString()}
            </div>
          </div>

          <Button
            variant="ghost"
            size="icon"
            onClick={onDelete}
            className="text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

function AddMemoryForm({ onSuccess, onCancel }: { onSuccess: () => void; onCancel: () => void }) {
  const [content, setContent] = useState('')
  const [category, setCategory] = useState('')
  const [tags, setTags] = useState('')
  const [importance, setImportance] = useState<'low' | 'medium' | 'high' | 'critical'>('medium')

  const createMutation = useMutation({
    mutationFn: (data: MemoryCreate) => api.memories.create(data),
    onSuccess: () => {
      onSuccess()
      setContent('')
      setCategory('')
      setTags('')
      setImportance('medium')
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim()) return

    const importanceMap = {
      low: 1,
      medium: 2,
      high: 3,
      critical: 4,
    }

    createMutation.mutate({
      content: content.trim(),
      category: category.trim() || undefined,
      tags: tags ? tags.split(',').map(t => t.trim()).filter(Boolean) : undefined,
      importance: importanceMap[importance],
      session_id: '1', // TODO: Get from current session
    })
  }

  return (
    <Card className="border-primary">
      <CardContent className="p-4">
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <Input
              placeholder="What do you want to remember?"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              required
              autoFocus
            />
          </div>

          <div className="flex gap-2">
            <Input
              placeholder="Category (optional)"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="flex-1"
            />
            <Input
              placeholder="Tags (comma-separated)"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              className="flex-1"
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Importance:</span>
            <div className="flex gap-1">
              {(['low', 'medium', 'high', 'critical'] as const).map((level) => (
                <Button
                  key={level}
                  type="button"
                  variant={importance === level ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setImportance(level)}
                >
                  {level}
                </Button>
              ))}
            </div>
          </div>

          <div className="flex gap-2 justify-end">
            <Button type="button" variant="outline" size="sm" onClick={onCancel}>
              Cancel
            </Button>
            <Button type="submit" size="sm" disabled={createMutation.isPending}>
              {createMutation.isPending ? 'Adding...' : 'Add Memory'}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
