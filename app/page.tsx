'use client';
import { useEffect, useRef, useState } from 'react';
import { Camera, ChevronLeft, ChevronRight, Expand, Code, Info, Map } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import { rooms, photoCaptions } from '@/lib/apartment-data';
import type { createRenderedTour } from '@/lib/tour-scene';

type Engine = ReturnType<typeof createRenderedTour>;
const repo = 'https://github.com/dylanxzthomas/apartment-virtual-tour';
const photos = photoCaptions.slice(0, 12);

export default function Home() {
  const host = useRef<HTMLDivElement>(null);
  const engine = useRef<Engine | null>(null);
  const shell = useRef<HTMLElement>(null);
  const [room, setRoom] = useState('living');
  const [ready, setReady] = useState(false);
  const [error, setError] = useState('');
  const [attempt, setAttempt] = useState(0);
  const [panel, setPanel] = useState<'photos' | 'notes' | null>(null);
  const [photo, setPhoto] = useState(1);
  const [mobileMap, setMobileMap] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const current = rooms.find(r => r.id === room) || rooms[0];

  useEffect(() => {
    let cancelled = false;
    setReady(false); setError('');
    setFullscreen(Boolean(document.fullscreenEnabled));
    import('@/lib/tour-scene').then(({ createRenderedTour }) => {
      if (cancelled || !host.current) return;
      engine.current = createRenderedTour(host.current,
        id => { if (!cancelled) setRoom(id); },
        () => { if (!cancelled) { setReady(true); setError(''); } },
        message => { if (!cancelled) setError(message); });
      engine.current.setFov(75);
    }).catch(() => { if (!cancelled) setError('The tour could not start. Please try again or explore the original photos.'); });
    return () => { cancelled = true; engine.current?.dispose(); engine.current = null; };
  }, [attempt]);

  const jump = (id: string) => { engine.current?.jump(id); setMobileMap(false); };
  const openPhotos = () => { setPhoto(current.photos[0] <= 12 ? current.photos[0] : 1); setPanel('photos'); };
  const step = (delta: number) => setPhoto(p => (p - 1 + delta + photos.length) % photos.length + 1);
  const navigation = <>
    <div className="mini-plan" aria-label="Apartment room map">
      <svg viewBox="-0.8 -4.5 8.4 17.9" role="img" aria-label="Apartment layout, with the current room highlighted">
        {rooms.map(r => { const [x, z, x1, z1] = r.bounds; return <g key={r.id}>
          <polygon points={r.polygon.map(p => p.join(',')).join(' ')} fill={r.id === room ? '#c4e1e5' : '#303a41'} stroke="#889298" strokeWidth=".055" />
          <text x={(x + x1) / 2} y={(z + z1) / 2 + .1} fill={r.id === room ? '#1a3c43' : '#e4eaec'} textAnchor="middle" fontSize=".29" fontFamily="Arial">{r.short}</text>
        </g>; })}
      </svg>
      {rooms.map(r => { const [x, z, x1, z1] = r.bounds; return <button key={r.id} className="plan-hit" onClick={() => jump(r.id)} aria-label={`Visit ${r.name}`} style={{ left: `${(x + .8) / 8.4 * 100}%`, top: `${(z + 4.5) / 17.9 * 100}%`, width: `${(x1 - x) / 8.4 * 100}%`, height: `${(z1 - z) / 17.9 * 100}%` }} />; })}
    </div>
    <div className="plan-legend">Select a room to step inside</div>
    <nav className="room-nav" aria-label="Rooms">{rooms.map((r, i) => <button key={r.id} className={r.id === room ? 'selected' : ''} aria-current={r.id === room ? 'location' : undefined} onClick={() => jump(r.id)}>
      <span className="room-number">{String(i + 1).padStart(2, '0')}</span><span>{r.name}</span>{r.id === room ? <span className="active-dot" /> : <ChevronRight size={14} />}
    </button>)}</nav>
  </>;

  return <main ref={shell} className="apartment-app">
    <header className="app-header">
      <div className="identity"><div className="unit-mark">04<span>UNIT</span></div><div><h1>2861 California</h1><p>4 bedrooms <span>·</span> 2 bathrooms <span>·</span> 1,140 sq ft</p></div></div>
      <div className="header-actions">
        <a className="github-link" href={repo} target="_blank" rel="noopener noreferrer" aria-label="View project on GitHub"><Code size={17} /><span>GitHub</span></a>
        <Button variant="ghost" onClick={() => setPanel('notes')} aria-label="About this project"><Info /><span>About</span></Button>
      </div>
    </header>
    <div className="workspace">
      <aside className="explorer"><div className="aside-heading">EXPLORE THE APARTMENT</div>{navigation}<div className="aside-bottom"><a href="https://x.com/dylan_szeto" target="_blank" rel="noopener noreferrer">A project by Dylan Szeto ↗</a></div></aside>
      <section className="viewport tour-view" aria-label="Apartment virtual tour">
        <div ref={host} className="scene-host" />
        <div className="view-toolbar"><span className="tour-mode-label">Virtual tour <span>360°</span></span>{fullscreen && <Button className="expand-button" variant="secondary" size="icon-lg" onClick={() => { if (document.fullscreenElement) void document.exitFullscreen(); else void shell.current?.requestFullscreen().catch(() => {}); }} aria-label="Toggle full screen"><Expand /></Button>}</div>
        {!ready && !error && <div className="scene-loading" role="status"><div className="loading-ring" />Opening your tour…</div>}
        {error && <div className="scene-error" role="alert"><p>{error}</p><Button onClick={() => setAttempt(n => n + 1)}>Try again</Button><Button onClick={openPhotos}>View original photos</Button></div>}
        <div className="scene-heading"><span>YOU ARE IN</span><h2 aria-live="polite">{current.name}</h2></div>
        <Button className="mobile-rooms" variant="secondary" onClick={() => setMobileMap(true)} aria-label="Choose a room"><Map />Rooms</Button>
        <div className="bottom-bar"><div className="view-hint"><span>Drag to look around</span><i /><span>Click a marker to move</span></div><Button className="reference-button" variant="secondary" onClick={openPhotos}><Camera />Original photos</Button></div>
      </section>
    </div>
    <Sheet open={mobileMap} onOpenChange={setMobileMap}><SheetContent side="left" className="room-sheet"><SheetHeader><SheetTitle>Explore the apartment</SheetTitle><SheetDescription>Choose a room to look around.</SheetDescription></SheetHeader>{navigation}</SheetContent></Sheet>
    <Sheet open={panel !== null} onOpenChange={v => { if (!v) setPanel(null); }}><SheetContent className={`reference-sheet ${panel === 'photos' ? 'photo-sheet' : ''}`}>
      <SheetHeader><SheetTitle>{panel === 'photos' ? 'The original photos' : 'About this project'}</SheetTitle><SheetDescription>{panel === 'photos' ? 'The 12 interior photos used to build this tour. Some room matches are approximate.' : 'An interactive tour of 2861 California, Unit 4.'}</SheetDescription></SheetHeader>
      {panel === 'photos' && <div className="photo-content"><div className="photo-stage"><img src={`/references/${String(photo).padStart(2, '0')}.png`} alt={photos[photo - 1]} /></div><div className="photo-caption"><div><span>PHOTO {String(photo).padStart(2, '0')} / 12</span><h3>{photos[photo - 1]}</h3></div><div><Button variant="outline" size="icon-lg" onClick={() => step(-1)} aria-label="Previous photograph"><ChevronLeft /></Button><Button variant="outline" size="icon-lg" onClick={() => step(1)} aria-label="Next photograph"><ChevronRight /></Button></div></div><div className="photo-grid">{photos.map((caption, i) => <button key={i} className={photo === i + 1 ? 'active' : ''} aria-pressed={photo === i + 1} onClick={() => setPhoto(i + 1)} aria-label={caption}><img src={`/references/${String(i + 1).padStart(2, '0')}.png`} alt="" loading="lazy" /><span>{String(i + 1).padStart(2, '0')}</span></button>)}</div></div>}
      {panel === 'notes' && <div className="notes-content">
        <p>I used AI and Blender to turn 12 interior photos and a floor plan into a 3D apartment. This tour brings the rooms together so you can understand the layout before stepping inside.</p>
        <h3>Take a look around</h3><p>Drag to turn your view. Click a marker or choose a room from the map to move to another spot. On a phone, tap <strong>Rooms</strong>. You can also scroll to zoom and use the arrow keys to look around.</p>
        <h3>A closer sense of the space</h3><p>The idea is to help people understand how an apartment fits together before visiting. The tour uses 11 carefully rendered viewpoints, including daylight and reflections.</p>
        <h3>What’s approximate</h3><p>This is a recreation, not a scan of the actual apartment. The layout follows the floor plan, but dimensions, some room details, and the views outside are estimated. The listed size is 1,140 square feet; it hasn’t been independently measured.</p>
        <h3>Curious how it was made?</h3><p>The code, source material, and editable 3D apartment are available on GitHub.</p>
        <div className="project-links"><a href={repo} target="_blank" rel="noopener noreferrer">Explore the code ↗</a><a href="/models/2861-california-unit-4.blend" download>Download the Blender model ↓</a></div>
        <p className="project-credit">Built by <a href="https://x.com/dylan_szeto" target="_blank" rel="noopener noreferrer">Dylan Szeto</a>.</p>
      </div>}
    </SheetContent></Sheet>
  </main>;
}
