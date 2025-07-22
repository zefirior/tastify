import {createRoot} from 'react-dom/client';
import './index.css';
import {StrictMode} from 'react';
import {BrowserRouter} from 'react-router';
import AppTheme from './components/theme/AppTheme.jsx';
import RouterSelector from './RouterSelector.jsx';

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <AppTheme>
            <BrowserRouter>
                <RouterSelector />
            </BrowserRouter>
        </AppTheme>
    </StrictMode>,
);
