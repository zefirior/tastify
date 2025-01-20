// import { StrictMode } from 'react'
import {createRoot} from 'react-dom/client';
import './index.css';
import {StrictMode} from 'react';
import {BrowserRouter, Route, Routes} from 'react-router';
// import MarketingPage from './marketing-page/MarketingPage.jsx';
import AppTheme from './components/theme/AppTheme.jsx';
import Room from './pages/Room.jsx';
import Home from './pages/Home.jsx';

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <AppTheme>
            <BrowserRouter>
                <Routes>
                    {/*<Route index element={<MarketingPage />} />*/}
                    <Route index element={<Home />} />
                    <Route path="room">
                        <Route path=":roomCode" element={<Room />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </AppTheme>
    </StrictMode>,
);
