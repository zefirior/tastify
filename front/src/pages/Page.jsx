import Footer from '../components/Footer.jsx';
import HeaderBar from '../components/HeaderBar.jsx';
import * as React from 'react';
import AppTheme from '../components/theme/AppTheme.jsx';
import CssBaseline from '@mui/material/CssBaseline';
import Divider from '@mui/material/Divider';

export default function Page(props) {
    return (
        <AppTheme {...props}>
            <CssBaseline enableColorScheme />
            <HeaderBar />
            <main className={'maim-content'}>
                {props.children}
                <Divider />
                {/*<Footer />*/}
            </main>
        </AppTheme>
    );
}