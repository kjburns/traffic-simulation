/*
 * Copyright 2019 Kevin J. Burns, P.E.
 * Contact: kevin.burns.pe at gmail dot com
 * This file is part of Traffic Simulation.
 * 
 * Traffic Simulation is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Traffic Simulation is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Traffic Simulation.  If not, see <https://www.gnu.org/licenses/>.
 */
package com.github.kjburns.traffic_simulation.network;

import java.awt.geom.Point2D;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Stream;

/**
 * Implementation of CurvatureCalculator.
 * @author Kevin J. Burns
 *
 */
public class CurvatureCalculatorImpl implements CurvatureCalculator {
	private class SegmentImpl implements Segment {
		private final double startSta;
		private final double endSta;
		private final int startVertex;
		private final double chordDirRadians;
		private final double radius;
		private final CurveDirection curveDirection;
		
		private SegmentImpl(final double startStation, final int startVtx) {
			startVertex = startVtx;

			startSta = startStation;
			endSta = calculateEndStation();
			chordDirRadians = calculateChordDirection();
			
			curveDirection = calculateCurveDirection();
			radius = calculateRadius();
		}
		
		private double calculateRadius() {
			if (!isInCurve()) {
				return Double.NaN;
			}
			
			final double[] angleBisectorDirections = new double[2];

			for (int i = 0; i < 2; i++) {
				final double delta = getDeflectionRadians(startVertex + i);
				final double backOrForward = (i == 0) ? -1.0 : +1.0;
				angleBisectorDirections[i] = getChordDirectionRadians() 
						+ Math.signum(delta) * (0.5 * Math.PI) 
						+ 0.5 * backOrForward * delta;
			}
			
			final double deflection = normalizeToDeflection(
					getEndAngleBisectorDirectionRadians() - getStartAngleBisectorDirectionRadians());
			return 0.5 * getChordLength() / Math.sin(0.5 * deflection);
		}

		private CurveDirection calculateCurveDirection() {
			if ((startVertex == 0) || getEndVertexNumber() == points.size() - 1) {
				// first and last segments are never curves
				return CurveDirection.NONE;
			}
			
			final double startDeflection = getDeflectionRadians(startVertex);
			final double endDeflection = getDeflectionRadians(startVertex + 1);
			
			if (startDeflection * endDeflection <= 0) {
				return CurveDirection.NONE;
			}
			
			if ((startDeflection >= 0) && (endDeflection >= 0)) {
				return CurveDirection.LEFT;
			}
			else {
				return CurveDirection.RIGHT;
			}
		}

		private double getDeflectionRadians(int piIndex) {
			final Point2D[] vectors = new Point2D[2];
			
			for (int i = 0; i < 2; i++) {
				Point2D first = points.get(piIndex + i - 1);
				Point2D second = points.get(piIndex + i);
				final double dx = second.getX() - first.getX();
				final double dy = second.getY() - first.getY();
				vectors[i] = new Point2D.Double(dx, dy);
			}
			
			final double angleA = Math.atan2(vectors[0].getY(), vectors[0].getX());
			final double angleB = Math.atan2(vectors[1].getY(), vectors[1].getX());
			
			final double theta = normalizeToDeflection(angleB - angleA);

			return theta;
		}

		private double normalizeToDeflection(double angle) {
			return Segment.normalizeAngle(angle, -Math.PI, Math.PI);
		}

		private double calculateChordDirection() {
			final Point2D start = points.get(startVertex);
			final Point2D end = points.get(startVertex + 1);
			
			final double dy = end.getY() - start.getY();
			final double dx = end.getX() - start.getX();
			
			return normalizeToDirection(Math.atan2(dy, dx));
		}

		private double normalizeToDirection(double angle) {
			return Segment.normalizeAngle(angle, 0, 2 * Math.PI);
		}
		
		private double calculateEndStation() {
			return startSta + getChordLength();
		}
		
		private double getChordLength() {
			final Point2D start = points.get(startVertex);
			final Point2D end = points.get(startVertex + 1);
			
			return start.distance(end);
		}

		@Override
		public double getStartStation() {
			return startSta;
		}

		@Override
		public double getEndStation() {
			return endSta;
		}

		@Override
		public int getStartVertexNumber() {
			return startVertex;
		}

		@Override
		public double getChordDirectionRadians() {
			return chordDirRadians;
		}

		@Override
		public double getRadius_rNaN() {
			return radius;
		}

		@Override
		public CurveDirection getCurveDirection() {
			return curveDirection;
		}

		@Override
		public boolean isInCurve() {
			return getCurveDirection() != CurveDirection.NONE;
		}

		@Override
		public double getStartAngleBisectorDirectionRadians() {
			final double delta = getDeflectionRadians(startVertex);
			final double backOrForward = -1.0;
			final double sign = (delta == 0.) ? -1. : Math.signum(delta);
			return getChordDirectionRadians() 
					+ sign * (0.5 * Math.PI) 
					+ 0.5 * backOrForward * delta;
		}

		@Override
		public double getEndAngleBisectorDirectionRadians() {
			final double delta = getDeflectionRadians(startVertex + 1);
			final double backOrForward = +1.0;
			final double sign = (delta == 0.) ? -1. : Math.signum(delta);
			return getChordDirectionRadians() 
					+ sign * (0.5 * Math.PI) 
					+ 0.5 * backOrForward * delta;
		}
	}
	
	private class SegmentCollectionImpl implements SegmentCollection {
		private final List<Segment> segments = new ArrayList<>();
		
		private final void add(Segment s) {
			segments.add(s);
		}
		
		@Override
		public Stream<Segment> stream() {
			return segments.stream();
		}
	}
	
	private final List<Point2D> points;
	private final SegmentCollectionImpl collection = new SegmentCollectionImpl();

	/**
	 * Creates a CurvatureCalculator from a list of points that approximate the road.
	 * @param points The points that define the road
	 */
	public CurvatureCalculatorImpl(List<Point2D> points) {
		this.points = Collections.unmodifiableList(points);
		
		buildCollection();
	}

	private void buildCollection() {
		double startStation = 0.;
		
		for (int i = 0; i < points.size() - 1; i++) {
			final Segment seg = this.new SegmentImpl(startStation, i);
			startStation = seg.getEndStation();
			collection.add(seg);
		}
	}

	@Override
	public final SegmentCollection getSegments() {
		return collection;
	}
}
