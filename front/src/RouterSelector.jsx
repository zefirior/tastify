import * as React from 'react';
import {Routes, Route, Navigate, useLocation} from 'react-router';
import HomeDesktop from './pages/desktop/Home.jsx';
import JoinRoom from './pages/desktop/JoinRoom.jsx';
import Room from './pages/desktop/Room.jsx';
import HomeMobile from './pages/mobile/Home.jsx';

function isMobile() {
    if (typeof navigator === 'undefined') return false;
    return /Mobi|Android/i.test(navigator.userAgent);
}

export default function RouterSelector() {
    const location = useLocation();
    const mobile = isMobile();

    if (mobile) {
        if (location.pathname !== '/') {
            return <Navigate to="/" replace />;
        }
        return (
            <Routes>
                <Route index element={<HomeMobile />} />
            </Routes>
        );
    }

    return (
        <Routes>
            <Route index element={<HomeDesktop />} />
            <Route path="room">
                <Route path=":roomCode" element={<Room />} />
                <Route path=":roomCode/join" element={<JoinRoom />} />
            </Route>
        </Routes>
    );
}
