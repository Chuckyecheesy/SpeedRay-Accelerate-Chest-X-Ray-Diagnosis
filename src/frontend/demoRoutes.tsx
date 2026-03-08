/** Demo-specific routes for SpeedRay */

import { Routes, Route } from 'react-router-dom';
import { ROUTES } from '../config';
import { DemoPage } from './DemoPage';

export function DemoRoutes() {
  return (
    <Routes>
      <Route path={ROUTES.DEMO} element={<DemoPage />} />
    </Routes>
  );
}
