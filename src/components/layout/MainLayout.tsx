import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function MainLayout() {
  return (
    <div className="flex h-screen w-screen bg-background">
      <Sidebar />
      <main className="flex-1 pl-24 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
