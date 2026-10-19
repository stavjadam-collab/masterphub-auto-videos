import React from 'react';
import { Composition } from 'remotion';
import { Promo, timeline } from './Promo';

export const Root: React.FC = () => (
  <>
    {['he', 'en', 'es', 'fr', 'pt', 'ar'].map((l) => (
      <Composition key={l} id={`VABPromo-${l}`} component={Promo} durationInFrames={timeline(l).total} fps={30} width={1080} height={1920} defaultProps={{ lang: l }} />
    ))}
  </>
);
