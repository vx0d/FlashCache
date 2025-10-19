# FlashCache

**FlashCache** is a lightweight Python library that speeds up functions by **caching results in memory**. It is ideal for heavy computations, API calls, or repeated database queries. By storing previously computed results, repeated calls return instantly, saving time and computational resources.

The library works seamlessly with both **synchronous and asynchronous functions** and provides flexible configuration options. You can set a **time-to-live (TTL)** for cached entries, limit memory usage with a **maximum cache size**, and choose from **eviction strategies** like LRU (Least Recently Used) or LFU (Least Frequently Used). FlashCache also includes built-in tools for managing cached data, such as clearing the cache, invalidating specific entries, and viewing cache statistics.

**For example**, if you have a function that performs heavy calculations, the first call will compute normally, while subsequent calls with the same inputs will return the result instantly from cache. Similarly, repeated API requests or database queries can be sped up, as results are stored and reused efficiently.

---

## Features

- Works with **regular and async functions**  
- Supports **TTL (time-to-live)** for automatic cache expiry  
- Limits memory usage with **max size** and **eviction strategies** (LRU / LFU)  
- Built-in **cache management**: clear cache, invalidate specific results, view stats  
- Simple **decorator-based usage**

---

## License

FlashCache is released under a **custom MIT-based license**. You are free to **use, modify, and include FlashCache in any project**, including commercial software.

**Rules:**  
1. **Attribution Required:** You must include this copyright notice and a link to the original repository in all copies or substantial portions: [https://github.com/vx0d/flashcache](https://github.com/vx0d/flashcache)  
2. **No Selling Standalone:** You may not sell FlashCache or license it as a standalone product. It must always be part of a software project or library.

FlashCache is provided **“as-is”**, without warranty of any kind.

---

## Analogy

Think of FlashCache like a sticky note for your functions:  
- First time a function runs, it calculates and writes the answer.  
- Next time, it just reads the note instead of recalculating.

