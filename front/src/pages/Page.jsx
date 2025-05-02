import HeaderBar from '../components/HeaderBar.jsx';
import * as React from 'react';
import AppTheme from '../components/theme/AppTheme.jsx';
import CssBaseline from '@mui/material/CssBaseline';
import UserSwitcher from "../components/debug-users/UserSwitcher.jsx";

export default function Page(props) {
    const enableUserSwitcher = import.meta.env['VITE_ENABLE_USER_SWITCHER'] === 'true' || false;

    return (
        <AppTheme {...props}>
            <CssBaseline enableColorScheme />
            <HeaderBar />
            {enableUserSwitcher && <UserSwitcher />}
            <main className={'main-content'}>
                {props.children}
            </main>
        </AppTheme>
    );
}