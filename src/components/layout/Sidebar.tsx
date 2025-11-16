import { Home, Tv, Settings, Flame } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import { cn } from '../../lib/utils';

const navItems = [
  { to: '/', icon: Home, label: 'Accueil' },
  { to: '/live', icon: Tv, label: 'En Direct' },
  { to: '/settings', icon: Settings, label: 'Paramètres' },
];

const NavItem = ({ to, icon: Icon, label }: typeof navItems[0]) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      cn(
        'flex flex-col items-center justify-center p-4 w-full text-gray-400 hover:bg-gray-700 hover:text-white transition-colors duration-200 focus:outline-none focus-visible:bg-gray-700 focus-visible:text-white',
        isActive && 'bg-gray-800 text-white border-l-4 border-red-600'
      )
    }
  >
    <Icon className="h-7 w-7 mb-1" />
    <span className="text-xs font-medium">{label}</span>
  </NavLink>
);

export function Sidebar() {
  return (
    <div className="fixed left-0 top-0 h-full w-24 bg-black flex flex-col items-center py-5 z-20">
      <div className="text-red-600 mb-10">
        <Flame size={40} />
      </div>
      <nav className="flex flex-col items-center w-full space-y-2">
        {navItems.map((item) => (
          <NavItem key={item.to} {...item} />
        ))}
      </nav>
    </div>
  );
}
