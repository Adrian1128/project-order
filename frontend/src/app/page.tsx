'use client';

import { useState } from 'react';

export default function Home() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();
      setResponse(data.response);
    } catch (error) {
      console.error("Failed to connect to backend:", error);
      setResponse("Error: Could not reach the backend server.");
    } finally {
      loading && setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-950 text-gray-100">
      <div className="w-full max-w-md space-y-4">
        <h1 className="text-2xl font-bold text-center">LLM Full-Stack Skeleton</h1>

        <form onSubmit={handleSubmit} className="flex flex-col gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message to the backend..."
            className="p-2 rounded bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-blue-500"
          />
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 p-2 rounded font-semibold transition"
          >
            {loading ? 'Sending...' : 'Send to Backend'}
          </button>
        </form>

        {response && (
          <div className="p-4 rounded bg-gray-900 border border-gray-800 mt-4">
            <p className="text-sm text-gray-400 mb-1">Backend Response:</p>
            <p className="text-white">{response}</p>
          </div>
        )}
      </div>
    </main>
  );
}