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

import java.util.Iterator;
import java.util.stream.Stream;

/**
 * Calculator to get approximate curve radii from a road that has 
 * been defined as a string of points only.
 * @author Kevin J. Burns
 *
 */
public interface CurvatureCalculator {
	/**
	 * A segment which connects two consecutive points on a point-defined road.
	 * @author Kevin J. Burns
	 *
	 */
	public interface Segment {
		/**
		 * Converts an angle (in radians) to its equivalent expression in the provided range.
		 * @param angle The angle to convert
		 * @param minInclusive The minimum value, inclusive, that this angle can take on.
		 * @param maxExclusive The maximum value, exclusive, that this angle can take on.
		 * @return The normalized angle. If the distance between minInclusive and maxExclusive
		 * is not 2π, the results may not be what you expect.
		 */
		public static double normalizeAngle(double angle, double minInclusive, double maxExclusive) {
			while (angle < minInclusive) {
				angle += 2. * Math.PI;
			}
			
			while (angle >= maxExclusive) {
				angle -= 2. * Math.PI;
			}

			return angle;
		}
		
		/**
		 * The direction that a segment is turning, when traveling
		 * the point list from beginning to end.
		 * @author Kevin J. Burns
		 *
		 */
		public enum CurveDirection {
			/**
			 * Not in a curve
			 */
			NONE,
			/**
			 * Deflecting left
			 */
			LEFT,
			/**
			 * Deflecting right
			 */
			RIGHT;
		}
		
		/**
		 * Gets the distance along the path from the start of the
		 * path to the start of this segment.
		 * @return
		 */
		double getStartStation();
		/**
		 * Gets the distance along the path from the start of the
		 * path to the end of this segment.
		 * @return
		 */
		double getEndStation();
		/**
		 * Gets the vertex number within the path at the start of this segment.
		 * @return
		 */
		int getStartVertexNumber();
		/**
		 * Gets the vertex number within the path at the end of this segment.
		 * @return
		 */
		default int getEndVertexNumber() {
			return getStartVertexNumber() + 1;
		}
		/**
		 * Gets the direction of this segment as a chord on the Cartesian plane.
		 * Zero is east, with positive angles measured anticlockwise.
		 * @return
		 */
		double getChordDirectionRadians();
		
		/**
		 * Direction of the angular bisector drawn from the start vertex
		 * on the side of the path on which the angle between this segment
		 * and the previous one is less than π. 
		 * If this segment and the previous one are collinear, the result will
		 * be to the right. 
		 * @return
		 */
		double getStartAngleBisectorDirectionRadians();
		/**
		 * Direction of the angular bisector drawn from the end vertex
		 * on the side of the path on which the angle between this segment
		 * and the next one is less than π. 
		 * If this segment and the next one are collinear, the result will
		 * be to the right. 
		 * @return
		 */
		double getEndAngleBisectorDirectionRadians();
		/**
		 * Gets the radius of the approximate arc formed by this segment. 
		 * <p>
		 * If {@link #isInCurve()} returns {@code false}, returns {@link Double#NaN}.
		 * </p>
		 * @return
		 */
		double getRadius_rNaN();
		/**
		 * Gets the direction of the approximate arc formed by this segment.
		 * @return
		 */
		CurveDirection getCurveDirection();
		/**
		 * Determines whether this segment can approximate an arc.
		 * @return
		 */
		boolean isInCurve();
	}
	
	/**
	 * A collection of segments.
	 * @author Kevin J. Burns
	 *
	 */
	public interface SegmentCollection {
		Stream<Segment> stream();
		
		default Iterator<Segment> iterator() {
			return stream().iterator();
		}
		
		/**
		 * Gets the segment that the supplied station falls in, or
		 * {@code null} if the supplied station does not exist within the collection.
		 * @param station
		 * @return
		 */
		default Segment getSegmentByStation_rNull(final double station) {
			return stream().filter((seg) -> {
				return (seg.getStartStation() - station) * (seg.getEndStation() - station) < 0;
			}).findFirst().orElse(null);
		}

		/**
		 * Gets the segment that starts with the supplied vertex number, or
		 * {@code null} if there is no such segment in the collection.
		 * @param vertexId
		 * @return
		 */
		default Segment getSegmentByStartVertexNumber_rNull(final int vertexId) {
			return stream().filter((seg) -> {
				return seg.getStartVertexNumber() == vertexId;
			}).findFirst().orElse(null);
		}
	}
	
	/**
	 * Gets the segments created by this curvature calculator.
	 * @return
	 */
	SegmentCollection getSegments();
}
