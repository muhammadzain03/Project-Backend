import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-app text-zinc-100">
      <div className="mx-auto max-w-3xl px-4 py-16 md:py-24">
        <p className="text-sm font-medium uppercase tracking-wide text-zinc-500 mb-3">
          SENG 533 — performance evaluation demo
        </p>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-4">
          ProfileHub
        </h1>
        <p className="text-lg text-zinc-400 mb-10 leading-relaxed">
          End-to-end performance evaluation of a cloud-based user authentication and profile
          management backend. This UI exercises the same REST API used in load tests.
        </p>

        <div className="panel p-6 md:p-8 mb-10 space-y-6">
          <div>
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wide mb-2">
              What it does
            </h2>
            <ul className="list-disc list-inside text-zinc-400 space-y-1 text-sm md:text-base">
              <li>Sign up and log in (bcrypt-hashed passwords, MySQL)</li>
              <li>Manage profile: avatar, text description, read-only account fields</li>
              <li>Store media and description JSON in Google Cloud Storage</li>
            </ul>
          </div>
          <div>
            <h2 className="text-sm font-semibold text-zinc-300 uppercase tracking-wide mb-2">
              Stack
            </h2>
            <p className="text-zinc-400 text-sm md:text-base leading-relaxed">
              <span className="text-zinc-300">Backend:</span> Flask, MySQL, GCS ·{' '}
              <span className="text-zinc-300">Frontend:</span> React, Vite, TypeScript, Tailwind
            </p>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3">
          <Link to="/signup">
            <Button
              size="lg"
              className="h-11 px-6 rounded-lg bg-white text-black hover:bg-zinc-200 w-full sm:w-auto"
            >
              Sign up <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </Link>
          <Link to="/login">
            <Button
              size="lg"
              variant="outline"
              className="h-11 px-6 rounded-lg border-zinc-700 bg-transparent text-zinc-200 hover:bg-zinc-800 w-full sm:w-auto"
            >
              Sign in
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
