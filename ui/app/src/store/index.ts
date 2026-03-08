/**
 * Redux Store Configuration
 *
 * Configures the Redux store with the L4 slice and necessary middleware.
 *
 * @module store/index
 */

import { configureStore } from '@reduxjs/toolkit';
import l4Reducer from './l4Slice';

export const store = configureStore({
  reducer: {
    l4: l4Reducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      // Enable serialization checks for development
      serializableCheck: {
        ignoredActions: ['l4/setCognitionData', 'l4/setWorkItem'],
      },
    }),
  devTools: true,
});

// Infer types from the store
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Typed hooks for use throughout the app
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';

export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
