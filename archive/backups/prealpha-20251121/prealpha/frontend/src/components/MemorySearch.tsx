import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, X, Calendar, Tag, Star } from 'lucide-react';
import { api } from '../services/api';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Card } from './ui/card';

interface SearchFilters {
  query: string;
  category?: string;
  minImportance?: number;
  dateFrom?: string;
  dateTo?: string;
  tags?: string[];
}

export function MemorySearch() {
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
  });
  const [showFilters, setShowFilters] = useState(false);
  const [activeSearch, setActiveSearch] = useState(false);

  // Fetch categories
  const { data: categoriesData } = useQuery({
    queryKey: ['memory-categories'],
    queryFn: async () => {
      const response = await api.get('/api/memories/categories');
      return response.data;
    },
  });

  // Fetch popular tags
  const { data: tagsData } = useQuery({
    queryKey: ['memory-tags'],
    queryFn: async () => {
      const response = await api.get('/api/memories/tags/popular?limit=10');
      return response.data;
    },
  });

  // Search query
  const { data: searchResults, isLoading, refetch } = useQuery({
    queryKey: ['memory-search', filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.query) params.append('query', filters.query);
      if (filters.category) params.append('category', filters.category);
      if (filters.minImportance) params.append('min_importance', filters.minImportance.toString());
      if (filters.dateFrom) params.append('date_from', filters.dateFrom);
      if (filters.dateTo) params.append('date_to', filters.dateTo);
      filters.tags?.forEach(tag => params.append('tags', tag));

      const response = await api.post(`/api/memories/search?${params.toString()}`);
      return response.data;
    },
    enabled: activeSearch,
  });

  const handleSearch = () => {
    setActiveSearch(true);
    refetch();
  };

  const handleClearFilters = () => {
    setFilters({ query: '' });
    setActiveSearch(false);
  };

  const addTagFilter = (tag: string) => {
    const currentTags = filters.tags || [];
    if (!currentTags.includes(tag)) {
      setFilters({ ...filters, tags: [...currentTags, tag] });
    }
  };

  const removeTagFilter = (tag: string) => {
    setFilters({
      ...filters,
      tags: filters.tags?.filter(t => t !== tag),
    });
  };

  const getImportanceColor = (importance: number) => {
    if (importance >= 4) return 'text-red-600';
    if (importance >= 3) return 'text-orange-600';
    return 'text-gray-600';
  };

  return (
    <div className="space-y-4 bg-[hsl(222.2,84%,4.9%)] text-[hsl(210,40%,98%)] min-h-[calc(100vh-4rem)] p-2 sm:p-0">
      {/* Search Bar */}
      <Card className="p-4 bg-[hsl(222.2,84%,4.9%)] text-[hsl(210,40%,98%)] border-[hsl(217.2,32.6%,17.5%)]">
        <div className="flex gap-2">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Search memories..."
              value={filters.query}
              onChange={(e) => setFilters({ ...filters, query: e.target.value })}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              className="pl-10"
            />
          </div>
          <Button onClick={handleSearch} disabled={isLoading} className="bg-[hsl(210,40%,98%)] text-[hsl(222.2,47.4%,11.2%)] hover:bg-[hsl(210,40%,95%)]">
            {isLoading ? 'Searching...' : 'Search'}
          </Button>
          <Button
            variant="outline"
            onClick={() => setShowFilters(!showFilters)}
            className="border-[hsl(217.2,32.6%,17.5%)] text-[hsl(210,40%,98%)] hover:bg-[hsl(217.2,32.6%,17.5%)]"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filters
          </Button>
          {activeSearch && (
            <Button
              variant="outline"
              onClick={handleClearFilters}
              className="border-[hsl(217.2,32.6%,17.5%)] text-[hsl(210,40%,98%)] hover:bg-[hsl(217.2,32.6%,17.5%)]"
            >
              <X className="w-4 h-4 mr-2" />
              Clear
            </Button>
          )}
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-4 pt-4 border-t border-[hsl(217.2,32.6%,17.5%)] space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <Tag className="inline w-4 h-4 mr-1" />
                  Category
                </label>
                <select
                  className="w-full px-3 py-2 border rounded-md bg-[hsl(222.2,84%,4.9%)] text-[hsl(210,40%,98%)] border-[hsl(217.2,32.6%,17.5%)]"
                  value={filters.category || ''}
                  onChange={(e) => setFilters({ ...filters, category: e.target.value || undefined })}
                >
                  <option value="">All Categories</option>
                  {categoriesData?.categories.map((cat: string) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              {/* Importance Filter */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <Star className="inline w-4 h-4 mr-1" />
                  Min Importance
                </label>
                <select
                  className="w-full px-3 py-2 border rounded-md bg-[hsl(222.2,84%,4.9%)] text-[hsl(210,40%,98%)] border-[hsl(217.2,32.6%,17.5%)]"
                  value={filters.minImportance || ''}
                  onChange={(e) => setFilters({ ...filters, minImportance: e.target.value ? parseInt(e.target.value) : undefined })}
                >
                  <option value="">Any</option>
                  <option value="1">1+</option>
                  <option value="2">2+</option>
                  <option value="3">3+</option>
                  <option value="4">4+</option>
                  <option value="5">5 (Critical)</option>
                </select>
              </div>

              {/* Date From */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <Calendar className="inline w-4 h-4 mr-1" />
                  From Date
                </label>
                <Input
                  type="date"
                  value={filters.dateFrom || ''}
                  onChange={(e) => setFilters({ ...filters, dateFrom: e.target.value || undefined })}
                />
              </div>

              {/* Date To */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  <Calendar className="inline w-4 h-4 mr-1" />
                  To Date
                </label>
                <Input
                  type="date"
                  value={filters.dateTo || ''}
                  onChange={(e) => setFilters({ ...filters, dateTo: e.target.value || undefined })}
                />
              </div>
            </div>

            {/* Tag Selection */}
            <div>
              <label className="block text-sm font-medium mb-2">
                Popular Tags (click to add)
              </label>
              <div className="flex flex-wrap gap-2">
                {tagsData?.tags.map((tagData: { tag: string; count: number }) => (
                  <Badge
                    key={tagData.tag}
                    variant="outline"
                    className="cursor-pointer hover:bg-[hsl(217.2,32.6%,17.5%)] border-[hsl(217.2,32.6%,17.5%)] text-[hsl(210,40%,98%)]"
                    onClick={() => addTagFilter(tagData.tag)}
                  >
                    {tagData.tag} ({tagData.count})
                  </Badge>
                ))}
              </div>
            </div>

            {/* Active Tag Filters */}
            {filters.tags && filters.tags.length > 0 && (
              <div>
                <label className="block text-sm font-medium mb-2">
                  Active Tag Filters
                </label>
                <div className="flex flex-wrap gap-2">
                  {filters.tags.map((tag) => (
                    <Badge
                      key={tag}
                      className="cursor-pointer bg-[hsl(217.2,32.6%,17.5%)] text-[hsl(210,40%,98%)]"
                      onClick={() => removeTagFilter(tag)}
                    >
                      {tag} <X className="inline w-3 h-3 ml-1" />
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Search Results */}
      {activeSearch && (
        <Card className="p-4 bg-[hsl(222.2,84%,4.9%)] text-[hsl(210,40%,98%)] border-[hsl(217.2,32.6%,17.5%)]">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">
              Search Results
              {searchResults && (
                <span className="text-sm font-normal text-gray-400 ml-2">
                  ({searchResults.count} found)
                </span>
              )}
            </h3>
          </div>

          {isLoading ? (
            <div className="text-center py-8 text-gray-400">
              Searching...
            </div>
          ) : searchResults?.results.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              No memories found. Try different search terms or filters.
            </div>
          ) : (
            <div className="space-y-3">
              {searchResults?.results.map((memory: any) => (
                <Card
                  key={memory.id}
                  className="p-4 hover:shadow-md transition-shadow bg-[hsl(222.2,84%,6%)] text-[hsl(210,40%,98%)] border-[hsl(217.2,32.6%,17.5%)]"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-sm mb-2">{memory.content}</p>
                      <div className="flex flex-wrap gap-2 items-center">
                        {memory.category && (
                          <Badge variant="outline" className="text-xs">
                            {memory.category}
                          </Badge>
                        )}
                        {memory.tags?.map((tag: string) => (
                          <Badge key={tag} className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                        <span className="text-xs text-gray-400">
                          {new Date(memory.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <div className="ml-4">
                      <Star
                        className={`w-4 h-4 ${getImportanceColor(memory.importance)}`}
                        fill="currentColor"
                      />
                      <span className={`text-xs ${getImportanceColor(memory.importance)}`}>
                        {memory.importance}
                      </span>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
