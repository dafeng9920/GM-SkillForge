/**
 * Main Entry Point
 *
 * Mounts the React application to the DOM.
 *
 * v1.0 路由结构：
 * - /execute/run-intent    执行意图
 * - /execute/import-skill  外部技能导入
 * - /audit/packs           AuditPack 浏览
 * - /audit/rag-query       RAG 查询
 * - /system/health         健康监控
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import { Provider } from 'react-redux';
import { RouterProvider } from 'react-router-dom';
import { store } from './store';
import { router } from './app/router';

import './styles/global.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Provider store={store}>
      <RouterProvider router={router} />
    </Provider>
  </React.StrictMode>
);
