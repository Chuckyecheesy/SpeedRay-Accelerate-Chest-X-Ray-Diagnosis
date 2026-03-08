/** Demo layout and navigation for SpeedRay */

import { Link, useLocation } from 'react-router-dom';
import { ROUTES } from '../config';
import styles from './DemoLayout.module.css';

export function DemoLayout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className={styles.layout}>
      <nav className={styles.nav}>
        <Link to={ROUTES.HOME} className={styles.brand}>
          SpeedRay
        </Link>
        <Link
          to={ROUTES.DEMO}
          className={location.pathname === ROUTES.DEMO ? styles.active : ''}
        >
          Demo
        </Link>
        <Link
          to={ROUTES.DASHBOARD}
          className={location.pathname === ROUTES.DASHBOARD ? styles.active : ''}
        >
          Dashboard
        </Link>
      </nav>
      <main className={styles.main}>{children}</main>
    </div>
  );
}
