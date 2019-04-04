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

import static org.junit.jupiter.api.Assertions.*;

import java.awt.geom.Point2D;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

import org.junit.jupiter.api.Test;

import com.github.kjburns.traffic_simulation.network.CurvatureCalculator.Segment;
import com.github.kjburns.traffic_simulation.network.CurvatureCalculator.Segment.CurveDirection;

class CurvatureCalculatorImplTest {
	private static final double MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE = 0.001;
	/*
	 * This is on US-71B going up the hill into downtown Fayetteville, Arkansas.
	 * Lat, Lon is 36.059467, -94.160951
	 */
	private static final String TEST_ROAD_SVG_PATH_D_ATTR = 
			"8.98024,416.0852 11.97367,80.82229 44.9013,86.80913 59.86835,65.855223 86.80916,44.9012801" + 
			" 89.80255,17.96051 368.1905,-14.96709 65.85521,17.9605099 80.822304,47.8947 56.874954,68.848627" +
			" 41.907861,89.80256 35.921024,92.79598 62.861797,74.83547 83.81572,41.90786 556.77588,200.55906" + 
			" 89.80254,35.92102 83.81574,68.84863 59.86836,92.79597 38.91439,107.76307 11.9737,122.73018" + 
			" 2.9935,194.5722";
	/*
	 * Should be ok to hardcode this hashcode since the algorithm of a String's
	 * hashcode computation is well defined.
	 */
	private static final int TEST_ROAD_SVG_PATH_D_ATTR_HASHCODE = 9898115;
	private static final List<Point2D> TRACED_POINTS = createPointList();
	private static final CurvatureCalculator CC = new CurvatureCalculatorImpl(TRACED_POINTS);
	private static final Comparator<? super Segment> SEGMENT_SORTER = (a, b) -> {
		return Integer.compare(a.getStartVertexNumber(), b.getStartVertexNumber());
	};
	
	private static List<Point2D> createPointList() {
		final List<Point2D> ret = new ArrayList<>();
		
		Point2D.Double currentLocation = new Point2D.Double(0., 0.);
		ret.add(currentLocation);
	
		final String[] pointsList = TEST_ROAD_SVG_PATH_D_ATTR.split(" ");
		for (String point : pointsList) {
			String[] ords = point.split(",");
			
			final double dx = Double.parseDouble(ords[0]);
			final double dy = Double.parseDouble(ords[1]);
			final double x = dx + currentLocation.getX();
			final double y = dy + currentLocation.getY();
			final Point2D.Double pt = new Point2D.Double(x, y);
			currentLocation = pt;
			
			ret.add(pt);
		}

		return ret;
	}

	@Test void testSegmentNormalizeAngle1() {
		final double expected = 1.;
		final double actual = CurvatureCalculator.Segment.normalizeAngle(1., -Math.PI, Math.PI);
		assertEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testSegmentNormalizeAngle2() {
		final double expected = Math.PI * 0.5;
		final double actual = CurvatureCalculator.Segment.normalizeAngle(Math.PI * 2.5, -Math.PI, Math.PI);
		assertEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testSegmentNormalizeAngle3() {
		final double expected = Math.PI * -0.75;
		final double actual = CurvatureCalculator.Segment.normalizeAngle(-2.75 * Math.PI, -Math.PI, Math.PI);
		assertEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}

	@Test void testThatRoadPointsAreValid() {
		final int expected = TEST_ROAD_SVG_PATH_D_ATTR_HASHCODE;
		final int actual = TEST_ROAD_SVG_PATH_D_ATTR.hashCode();
		assertEquals(expected, actual);
	}
	
	@Test void testThatRoadPointsAreAsExpected() {
		final double[] expected = {
				0, 425.06544, 517.8614, 649.57183, 775.295403, 907.0058431, 1014.7689031, 
				1367.9923131, 1451.808033, 1580.525037, 1706.248618, 1837.959039, 1966.676043, 
				2104.37331, 2230.09689, 2987.43183, 3113.15539, 3265.81976, 3418.48409, 
				3565.16155, 3699.86543, 3897.43113
		};
		final double[] actual = TRACED_POINTS.stream().mapToDouble((pt) -> {
			return pt.getX() + pt.getY();
		}).toArray();
		assertArrayEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testThatPointCountIsCorrect() {
		final int expected = 22;
		final int actual = TRACED_POINTS.size();
		assertEquals(expected, actual);
	}
	
	@Test void testThatSegmentCountIsCorrect() {
		final int expected = 21;
		final int actual = (int)CC.getSegments().stream().count();
		assertEquals(expected, actual);
	}
	
	@Test void testThatSegmentStartStationIsCorrect() {
		final double[] expected = {
				0, 416.182097608123, 497.886512018319, 595.620599178567, 684.621327985146, 782.355432649405, 
				873.936423613483, 1242.43100711956, 1310.69145393917, 1404.63903034196, 1493.94129141237, 
				1593.0410825128, 1692.54693093071, 1790.28102473727, 1883.98984848882, 2475.78653409787, 
				2572.50683118329, 2680.97439372908, 2791.40678289698, 2905.98081575302, 3029.29369656651
		};
		final double[] actual = CC.getSegments().stream().sorted(SEGMENT_SORTER).mapToDouble((seg) -> {
			return seg.getStartStation();
		}).toArray();
		assertArrayEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testThatSegmentEndStationIsCorrect() {
		final double[] expected = {
				416.182097608123, 497.886512018319, 595.620599178567, 684.621327985146, 782.355432649405, 
				873.936423613483, 1242.43100711956, 1310.69145393917, 1404.63903034196, 1493.94129141237, 
				1593.0410825128, 1692.54693093071, 1790.28102473727, 1883.98984848882, 2475.78653409787, 
				2572.50683118329, 2680.97439372908, 2791.40678289698, 2905.98081575302, 3029.29369656651, 
				3223.88892275433};
		final double[] actual = CC.getSegments().stream().sorted(SEGMENT_SORTER).mapToDouble((seg) -> {
			return seg.getEndStation();
		}).toArray();
		assertArrayEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testThatSegmentChordDirectionIsCorrect() {
		final double expected[] = {
				1.54921698194064, 1.42371800279527, 1.09345070938403, 0.832981553880689, 0.477345295535278, 
				0.197395559849881, 6.24255727897746, 0.266252022040169, 0.534955085995623, 0.880349858854901, 
				1.1341691700294, 1.20146267395843, 0.872136484837374, 0.463647609000806, 0.345745958245118, 
				0.380506415510787, 0.687671159355454, 0.997830242815741, 1.22425788878, 1.47354293562357, 
				1.55541250604815
		};
		final double actual[] = CC.getSegments().stream().sorted(SEGMENT_SORTER).mapToDouble((seg) -> {
			return seg.getChordDirectionRadians();
		}).toArray();
		assertArrayEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testThatSegmentStartAngleBisectorIsCorrect() {
		final double[] expected = {
				6.19885647275265, 5.97097333647434, 5.67560511201705, 5.36755240509267, 5.04975940807727, 
				4.79077274620857, 1.68360832371392, 1.97139988081279, 2.27844879922016, 2.57805584123705, 
				2.73861224878881, 5.74918855978259, 5.38028102730378, 5.11708576400765, 1.93392251367285, 
				2.10488511422802, 2.41354702788049, 2.68184039259277, 2.91969673899668
		};
		final double[] actual = CC.getSegments().stream().filter((seg) -> {
			return (seg.getStartVertexNumber() > 0) && (seg.getEndVertexNumber() < TRACED_POINTS.size() - 1);
		}).sorted(SEGMENT_SORTER).mapToDouble((seg) -> {
			return Segment.normalizeAngle(seg.getStartAngleBisectorDirectionRadians(), 0, 2 * Math.PI);
		}).toArray();
		assertArrayEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testThatSegmentEndAngleBisectorIsCorrect() {
		final double[] expected = {
				5.97097333647434, 5.67560511201705, 5.36755240509267, 5.04975940807727, 4.79077274620857, 
				1.68360832371392, 1.97139988081279, 2.27844879922016, 2.57805584123705, 2.73861224878881, 
				5.74918855978259, 5.38028102730378, 5.11708576400765, 1.93392251367285, 2.10488511422802, 
				2.41354702788049, 2.68184039259277, 2.91969673899668, 3.08527404763076
		};
		final double[] actual = CC.getSegments().stream().filter((seg) -> {
			return (seg.getStartVertexNumber() > 0) && (seg.getEndVertexNumber() < TRACED_POINTS.size() - 1);
		}).sorted(SEGMENT_SORTER).mapToDouble((seg) -> {
			return Segment.normalizeAngle(seg.getEndAngleBisectorDirectionRadians(), 0, 2 * Math.PI);
		}).toArray();
		assertArrayEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
	
	@Test void testThatCurveDirectionIsCorrect() {
		CurveDirection[] expected = {
				CurveDirection.NONE, CurveDirection.RIGHT, CurveDirection.RIGHT, CurveDirection.RIGHT, 
				CurveDirection.RIGHT, CurveDirection.RIGHT, CurveDirection.NONE, CurveDirection.LEFT, 
				CurveDirection.LEFT, CurveDirection.LEFT, CurveDirection.LEFT, CurveDirection.NONE, 
				CurveDirection.RIGHT, CurveDirection.RIGHT, CurveDirection.NONE, CurveDirection.LEFT, 
				CurveDirection.LEFT, CurveDirection.LEFT, CurveDirection.LEFT, CurveDirection.LEFT, 
				CurveDirection.NONE
		};
		CurveDirection[] actual = {};
		actual = CC.getSegments().stream().map((seg) -> {
			return seg.getCurveDirection();
		}).collect(Collectors.toList()).toArray(actual);
		assertArrayEquals(expected, actual);
	}
	
	@Test void testThatIsInCurveIsCorrect() {
		Boolean[] expected = {
				false, true, true, true, true, true, false, true, true, true, true, false, 
				true, true, false, true, true, true, true, true, false
		};
		Boolean[] actual = {};
		actual = CC.getSegments().stream().map((seg) -> {
			return seg.isInCurve();
		}).collect(Collectors.toList()).toArray(actual);
		
		assertArrayEquals(expected, actual);
	}
	
	@Test void testThatRadiusIsCorrect() {
		double[] expected = {
				Double.NaN, -359.313437054307, -332.094850665902, -290.059505692255, -308.83810199612, 
				-354.602967677873, Double.NaN, 238.007621070108, 307.174660888635, 299.18236823135, 
				617.890719026329, Double.NaN, -266.436700853822, -357.072707004857, Double.NaN, 
				566.429074630607, 352.811079353781, 412.847694649707, 482.831626782096, 745.596471946969, 
				Double.NaN
		};
		double[] actual = CC.getSegments().stream().mapToDouble((seg) -> {
			return seg.getRadius_rNaN();
		}).toArray();
		assertArrayEquals(expected, actual, MAX_DELTA_FOR_ASSERTEQUALS_DOUBLE);
	}
}
