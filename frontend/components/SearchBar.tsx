"use client";

interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  onSearch: (q: string) => void;
  isSearching: boolean;
}

export default function SearchBar({
  query,
  setQuery,
  onSearch,
  isSearching,
}: SearchBarProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isSearching) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full max-w-4xl mx-auto" aria-label="Search query input">
      <div className="relative rounded-2xl bg-black/70 backdrop-blur-2xl border border-[#06B6D4]/40 p-2 shadow-[0_0_30px_rgba(6,182,212,0.2)] focus-within:border-[#06B6D4] focus-within:shadow-[0_0_40px_rgba(6,182,212,0.4)] transition-all duration-300">
        <label htmlFor="search-input" className="sr-only">
          Search query
        </label>
        <input
          id="search-input"
          type="text"
          className="w-full px-6 py-5 bg-transparent text-white font-mono text-lg sm:text-xl placeholder-gray-500 outline-none focus-visible:ring-2 focus-visible-ring-[#06B6D4]"
          placeholder='Try "speaker discussing transformers" or "prompt engineering"...'
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          autoFocus
          disabled={isSearching}
          aria-label="Search query"
          aria-disabled={isSearching}
        />
        <button
          type="submit"
          disabled={!query.trim() || isSearching}
          className="absolute right-4 top-1/2 -translate-y-1/2 px-8 py-3.5 bg-[#06B6D4] hover:bg-[#10B981] disabled:opacity-40 disabled:cursor-not-allowed text-black font-mono font-black text-sm tracking-wider uppercase rounded-xl transition-all shadow-md cursor-pointer focus-visible:ring-2 focus-visible:ring-[#06B6D4]"
          aria-label={isSearching ? "Search in progress" : "Search"}
        >
          {isSearching ? "INFERRING..." : "SEARCH"}
        </button>
      </div>
    </form>
  );
}
