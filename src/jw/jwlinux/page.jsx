'use client';

import { useState, useEffect } from 'react';

export default function JWLibraryLinuxWelcome() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [isCompatible, setIsCompatible] = useState(null);
  const [mounted, setMounted] = useState(false);

  const screenshots = [
    {
      title: "JW Library Running on Ubuntu",
      description: "Full functionality with publications, videos, and audio",
      image: "/images/jwlibrary-ubuntu.png"
    },
    {
      title: "Desktop Integration",
      description: "Appears in your applications menu like any native app",
      image: "/images/jwlibrary-menu.png"
    },
    {
      title: "Complete Library Access",
      description: "Access all publications, study tools, and media",
      image: "/images/jwlibrary-features.png"
    }
  ];

  const supportedDistros = [
    {
      name: "Ubuntu",
      versions: ["20.04 LTS", "22.04 LTS", "24.04 LTS"],
      logo: "🟠",
      tested: true,
      popularity: "Most Popular"
    },
    {
      name: "Linux Mint",
      versions: ["20.x", "21.x", "22.x"],
      logo: "🟢",
      tested: true,
      popularity: "Beginner Friendly"
    },
    {
      name: "Debian",
      versions: ["10 (Buster)", "11 (Bullseye)", "12 (Bookworm)"],
      logo: "🔴",
      tested: true,
      popularity: "Stable"
    },
    {
      name: "Fedora",
      versions: ["37", "38", "39", "40+"],
      logo: "🔵",
      tested: true,
      popularity: "Latest Features"
    },
    {
      name: "Arch Linux",
      versions: ["Rolling Release"],
      logo: "⚫",
      tested: true,
      popularity: "Advanced Users"
    },
    {
      name: "openSUSE",
      versions: ["Leap 15.4+", "Tumbleweed"],
      logo: "🟢",
      tested: false,
      popularity: "May Work"
    }
  ];

  const features = [
    {
      icon: "⚡",
      title: "One-Click Installation",
      description: "Download and run our installer script — everything is automated"
    },
    {
      icon: "🍷",
      title: "Wine Pre-Configured",
      description: "We handle all Wine setup, dependencies, and optimization for you"
    },
    {
      icon: "🖥️",
      title: "Desktop Integration",
      description: "JW Library appears in your applications menu like a native app"
    },
    {
      icon: "🔄",
      title: "Automatic Updates",
      description: "Easy update mechanism to get the latest JW Library version"
    },
    {
      icon: "🗑️",
      title: "Clean Uninstall",
      description: "Remove everything completely with our uninstaller script"
    },
    {
      icon: "📱",
      title: "Full Functionality",
      description: "Publications, videos, audio, annotations — everything works"
    }
  ];

  const requirements = [
    "64-bit Linux system (x86_64 architecture)",
    "At least 4GB RAM (8GB recommended)",
    "2GB free disk space",
    "Internet connection for installation",
    "Administrator/sudo privileges",
    "Graphics drivers properly installed"
  ];

  useEffect(() => {
    setMounted(true);
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % screenshots.length);
    }, 5000);
    return () => clearInterval(interval);
  }, [screenshots.length]);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const userAgent = navigator.userAgent.toLowerCase();
      const isLinux = userAgent.includes('linux') && !userAgent.includes('android');
      const is64Bit = userAgent.includes('x86_64') || userAgent.includes('amd64');
      setIsCompatible(isLinux && is64Bit);
    }
  }, []);

  const scrollToRequirements = () => {
    const element = document.getElementById('requirements');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  if (!mounted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="w-6 h-6 border-2 border-gray-300 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white font-system">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-white/80 backdrop-blur-xl border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                <span className="text-white font-semibold text-sm">RD</span>
              </div>
              <span className="text-xl font-semibold text-black">RodgersDigital</span>
            </div>
            <div className="flex items-center space-x-8">
              <a href="/" className="text-gray-600 font-medium hover:text-black transition-colors duration-200">
                Home
              </a>              
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-6 py-32 bg-white">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8">
            <span className="inline-block bg-gray-100 text-gray-600 px-4 py-2 rounded-full text-sm font-medium">
              🐧 Linux Compatible Tool
            </span>
          </div>
          
          <h2 className="text-4xl md:text-5xl font-light mb-6 tracking-tight">
              JW Library for Linux
          </h2>
          
          <p className="text-xl text-gray-600 mb-12 max-w-2xl mx-auto leading-relaxed font-light">
            Install JW Library on any Linux distribution with our automated installer. 
            No Wine expertise required — we handle everything for you.
          </p>

          {/* Compatibility Check */}
          {isCompatible !== null && (
            <div className={`inline-flex items-center px-6 py-3 rounded-full mb-12 ${
              isCompatible 
                ? 'bg-green-50 text-green-700 border border-green-200' 
                : 'bg-orange-50 text-orange-700 border border-orange-200'
            }`}>
              <span className="text-xl mr-3">
                {isCompatible ? '✅' : '⚠️'}
              </span>
              <span className="font-medium">
                {isCompatible 
                  ? 'Your system appears compatible!' 
                  : 'Please check system requirements below'
                }
              </span>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-8">
            <a href="/jwlibrarylinuxinstaller">
              <button className="bg-blue-500 text-white px-8 py-4 rounded-full text-lg font-medium hover:bg-blue-600 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5">
                Get Started — Free Download
              </button>
            </a>
            
            <button 
              onClick={scrollToRequirements}
              className="text-blue-500 px-8 py-4 rounded-full text-lg font-medium hover:bg-blue-50 transition-all duration-200"
            >
              Check Compatibility
            </button>
          </div>

          <div className="text-sm text-gray-500">
            Free tool • No registration required • Open source approach
          </div>
        </div>
      </section>

      {/* Spacing between sections */}
      <div className="h-16 bg-gradient-to-b from-white to-gray-50"></div>

      {/* Screenshot Carousel */}
      <section className="py-32 px-6 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-light text-black text-center mb-16 tracking-tight">
            See JW Library running on Linux.
          </h2>
          
          <div className="bg-white rounded-3xl p-8 shadow-xl">
            <div className="relative h-96 bg-gray-100 rounded-2xl overflow-hidden">
              {/* Placeholder for screenshots */}
              <div className="w-full h-full flex items-center justify-center">
                <div className="text-center">
                  <div className="text-6xl mb-6">📱</div>
                  <h3 className="text-2xl font-medium text-black mb-3">
                    {screenshots[currentSlide].title}
                  </h3>
                  <p className="text-gray-600 font-light">
                    {screenshots[currentSlide].description}
                  </p>
                </div>
              </div>
            </div>
            
            {/* Slide indicators */}
            <div className="flex justify-center mt-8 space-x-2">
              {screenshots.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentSlide(index)}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    index === currentSlide ? 'bg-blue-500 w-8' : 'bg-gray-300'
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Spacing between sections */}
      <div className="h-16 bg-gradient-to-b from-gray-50 to-white"></div>

      {/* Features Grid */}
      <section className="py-32 px-6 bg-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-light text-black text-center mb-16 tracking-tight">
            Why choose our installer?
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center group">
                <div className="text-4xl mb-6">{feature.icon}</div>
                <h3 className="text-xl font-medium text-black mb-4">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed font-light">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Spacing between sections */}
      <div className="h-16 bg-gradient-to-b from-white to-gray-50"></div>

      {/* Supported Distributions */}
      <section className="py-32 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-light text-black text-center mb-16 tracking-tight">
            Supported Linux distributions.
          </h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {supportedDistros.map((distro, index) => (
              <div key={index} className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-shadow duration-200">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{distro.logo}</span>
                    <h3 className="text-xl font-medium text-black">
                      {distro.name}
                    </h3>
                  </div>
                  <span className={`text-xs px-3 py-1 rounded-full font-medium ${
                    distro.tested 
                      ? 'bg-green-100 text-green-700' 
                      : 'bg-orange-100 text-orange-700'
                  }`}>
                    {distro.popularity}
                  </span>
                </div>
                
                <div className="space-y-1 mb-4">
                  {distro.versions.map((version, vIndex) => (
                    <div key={vIndex} className="text-sm text-gray-600 font-light">
                      • {version}
                    </div>
                  ))}
                </div>
                
                <div className={`text-sm font-medium ${
                  distro.tested ? 'text-green-600' : 'text-orange-600'
                }`}>
                  {distro.tested ? '✅ Fully Tested' : '⚠️ Should Work'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Spacing between sections */}
      <div className="h-16 bg-gradient-to-b from-gray-50 to-white"></div>

      {/* System Requirements */}
      <section id="requirements" className="py-32 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-4xl md:text-5xl font-light text-black text-center mb-16 tracking-tight">
            System requirements.
          </h2>
          
          <div className="bg-white rounded-3xl p-8 shadow-xl">
            <div className="grid md:grid-cols-2 gap-12">
              <div>
                <h3 className="text-xl font-medium text-black mb-6 flex items-center">
                  <span className="mr-3">✅</span>
                  Minimum Requirements
                </h3>
                <ul className="space-y-3">
                  {requirements.map((req, index) => (
                    <li key={index} className="text-gray-600 flex items-start font-light">
                      <span className="text-gray-400 mr-3 mt-1.5 text-xs">●</span>
                      {req}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h3 className="text-xl font-medium text-black mb-6 flex items-center">
                  <span className="mr-3">⚡</span>
                  Installation Process
                </h3>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-4 mt-0.5 flex-shrink-0">1</span>
                    <div>
                      <div className="text-black font-medium">Download Script</div>
                      <div className="text-gray-600 text-sm font-light">One-click download from our tool</div>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-4 mt-0.5 flex-shrink-0">2</span>
                    <div>
                      <div className="text-black font-medium">Run Installer</div>
                      <div className="text-gray-600 text-sm font-light">Automated Wine setup and configuration</div>
                    </div>
                  </div>
                  <div className="flex items-start">
                    <span className="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm font-medium mr-4 mt-0.5 flex-shrink-0">3</span>
                    <div>
                      <div className="text-black font-medium">Launch JW Library</div>
                      <div className="text-gray-600 text-sm font-light">Find it in your applications menu</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Spacing between sections */}
      <div className="h-16 bg-gradient-to-b from-white to-black"></div>

      {/* Call to Action */}
      <section className="py-32 px-6 bg-black text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-light mb-6 tracking-tight">
            Ready to install JW Library?
          </h2>
          <p className="text-xl mb-12 max-w-2xl mx-auto leading-relaxed font-light text-gray-300">
            Join thousands of Linux users who have successfully installed JW Library with our tool.
          </p>
          
          <a href="/jwlibrarylinuxinstaller">
            <button className="bg-white text-black px-12 py-4 rounded-full text-lg font-medium hover:bg-gray-100 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 mb-8">
              Start Installation Now
            </button>
          </a>
          
          <div className="text-sm text-gray-400 space-y-2 font-light">
            <div>Free forever • No registration required • No data collection</div>
            <div>Made with care for the Linux community by RodgersDigital</div>
          </div>
        </div>
      </section>

      {/* Spacing between sections */}
      <div className="h-16 bg-gradient-to-b from-black to-gray-50"></div>

      {/* Footer Grid */}
      <section className="py-32 px-6 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-12 mb-12">

            <div className="max-w-xs">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                  <span className="text-white font-semibold text-sm">RD</span>
                </div>
                <span className="text-xl font-semibold text-black">RodgersDigital</span>
              </div>
              <p className="text-gray-600 font-light leading-relaxed">
                Creating useful tools and solutions for developers and technology enthusiasts worldwide.
              </p>
            </div>

            <div className="max-w-xs">
              <h4 className="text-black font-medium mb-4">Useful Links</h4>
              <ul className="space-y-3">
                <li><a href="/jwlibrarylinuxinstaller" className="text-gray-600 hover:text-black transition-colors duration-200 font-light">Installation Tool</a></li>
                <li><a href="https://rodgersdigital.com" className="text-gray-600 hover:text-black transition-colors duration-200 font-light">Main Website</a></li>
                <li><a href="mailto:support@rodgersdigital.com" className="text-gray-600 hover:text-black transition-colors duration-200 font-light">Get Support</a></li>
              </ul>
            </div>

            <div className="max-w-xs">
              <h4 className="text-black font-medium mb-4">About This Tool</h4>
              <ul className="space-y-2 text-gray-600 font-light">
                <li>Open source approach</li>
                <li>Community driven</li>
                <li>Regularly updated</li>
                <li>Free to use</li>
              </ul>
            </div>
        </div>
        <div className="border-t border-gray-200 pt-8 text-center">
            <p className="text-gray-500 font-light">
              © 2025 RodgersDigital. This tool is provided free of charge to the brothers.
            </p>
        </div>
        </div>
      </section>
  </div>
  );
}