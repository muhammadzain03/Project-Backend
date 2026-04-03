import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { LogOut, User } from 'lucide-react';

export default function Layout() {
  const { userEmail, logout } = useAuth();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-app text-zinc-100">
      <header className="sticky top-0 z-50 w-full border-b border-zinc-800 bg-zinc-950/95">
        <div className="container mx-auto flex h-14 items-center justify-between px-4 md:px-8">
          <Link
            to="/"
            className="flex items-center gap-2 font-semibold tracking-tight text-white hover:text-zinc-200"
          >
            <User className="h-5 w-5 text-blue-500" aria-hidden />
            <span className="text-lg">ProfileHub</span>
          </Link>

          <div className="flex items-center gap-3">
            {userEmail ? (
              <>
                <Link to="/dashboard">
                  <Button variant="ghost" className="text-zinc-300 hover:text-white hover:bg-zinc-800 rounded-lg">
                    Dashboard
                  </Button>
                </Link>
                <span className="text-sm text-zinc-500 hidden sm:inline max-w-[200px] truncate">
                  {userEmail}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="gap-2 text-zinc-300 hover:text-white hover:bg-zinc-800 rounded-lg"
                >
                  <LogOut className="h-4 w-4" />
                  <span className="hidden sm:inline">Logout</span>
                </Button>
              </>
            ) : (
              <>
                <Link to="/login">
                  <Button variant="ghost" className="text-zinc-300 hover:text-white hover:bg-zinc-800 rounded-lg">
                    Sign In
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button className="rounded-lg bg-white text-black hover:bg-zinc-200">Sign up</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="min-h-[calc(100vh-3.5rem)] flex flex-col">
        <div key={location.pathname} className="flex-1 flex flex-col">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
