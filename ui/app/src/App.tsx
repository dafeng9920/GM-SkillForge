/**
 * L4 Workbench Application
 *
 * Main application component for the L4 Dual-Window Frontend.
 *
 * @module App
 */

import React from 'react';
import { L4Workbench } from './views';

// App container styles
const appContainerStyles: React.CSSProperties = {
  height: '100vh',
  width: '100vw',
  overflow: 'hidden',
};

export const App: React.FC = () => {
  return (
    <div style={appContainerStyles}>
      <L4Workbench />
    </div>
  );
};

export default App;
