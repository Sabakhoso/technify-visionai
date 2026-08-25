import { NavLink } from 'react-router-dom'
import { LayoutDashboard, ListVideo, Camera } from 'lucide-react'
import './Sidebar.css'

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-mark">TV</div>
        <span className="sidebar-brand-name">Technify VisionAI</span>
      </div>

      <nav className="sidebar-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
        >
          <LayoutDashboard size={18} strokeWidth={1.75} />
          <span>Dashboard</span>
        </NavLink>

        <NavLink
          to="/events"
          className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
        >
          <ListVideo size={18} strokeWidth={1.75} />
          <span>Events</span>
        </NavLink>

        <NavLink
          to="/cameras"
          className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
        >
          <Camera size={18} strokeWidth={1.75} />
          <span>Cameras</span>
        </NavLink>
      </nav>
    </aside>
  )
}

export default Sidebar