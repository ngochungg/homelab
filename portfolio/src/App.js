import logo from './logo.svg';
import './App.css';
import { ReactTyped } from 'react-typed';
import { Menu, MenuItem, MenuButton } from '@szhsin/react-menu';
import '@szhsin/react-menu/dist/index.css';
import '@szhsin/react-menu/dist/transitions/zoom.css';

function App() {  
  return (
    <div className="flex flex-col items-center justify-center h-screen px-4">
      <div className='absolute top-0 right-0 w-1/12 pt-8 flex flex-col items-center justify-center'>
        <Menu menuButton=
          {<MenuButton className="flex items-center gap-2">
            <div className="flex flex-col">
              <div className="menu_icon"></div>
              <div className="menu_icon"></div>
            </div>
            <div className="menu-text pl-3">Menu</div>
          </MenuButton>} transition>
          <MenuItem>Cut</MenuItem>
          <MenuItem>Copy</MenuItem>
          <MenuItem>Paste</MenuItem>
        </Menu>
      </div>
      <div className="flex items-center justify-center h-screen px-4">
        <div className="flex flex-col md:flex-row items-center justify-center gap-8 max-w-5xl w-full">
          {/* Left Side */}
          <div className='md:w-1/2 flex flex-col items-center md:items-start text-center'>
            <div className='element-div-header md:text-left w-full'>
              <ReactTyped 
                strings={['I\'M Hung', '私は Hung', '我是 Hung']} 
                typeSpeed={150} 
                backSpeed={50} 
                backDelay={3000}
                loop 
              />
            </div>
            <code className='element-div-p mb-4 md:text-left w-full'>
              Computer Science Student | Cybersecurity Enthusiast | Software Developer
            </code>
            <div className='element-div-p mt-4 mb-4 md:text-left w-full'>
              A Computer Science student and software developer passionate about building intelligent software, 
              self-hosted systems, automation workflows, cybersecurity, and homelab experimentation.
            </div>
          </div>
          {/* Right Side */}
          <div className='md:w-1/2 flex justify-center gap-4'>
            <img 
              src={logo} 
              alt="Avatar" 
              className='w-48 h-48 rounded-full object-cover'
            />
            <img 
              src={logo} 
              alt="Avatar" 
              className='w-48 h-48 rounded-full object-cover'
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
