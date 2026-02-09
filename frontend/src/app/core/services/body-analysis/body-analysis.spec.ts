import { TestBed } from '@angular/core/testing';

import { BodyAnalysis } from './body-analysis';

describe('BodyAnalysis', () => {
  let service: BodyAnalysis;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BodyAnalysis);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
