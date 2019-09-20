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
package com.github.kjburns.traffic_simulation.parameters;

import static org.junit.jupiter.api.Assertions.*;

import java.io.InputStream;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class BinnedDistributionXmlTest {
	private Distribution<Double> freeFlowSpeedDistr;
	private Distribution<Double> laneChangeDistanceDistr;
	private Distribution<Double> irregularBinsDistr;

	public BinnedDistributionXmlTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/BinnedDistributionTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("binned-distribution");
			freeFlowSpeedDistr = 
					RealNumberDistributionFactory.createDistribution((Element)nodes.item(0));
			laneChangeDistanceDistr = 
					RealNumberDistributionFactory.createDistribution((Element)nodes.item(1));
			irregularBinsDistr =
					RealNumberDistributionFactory.createDistribution((Element)nodes.item(2));
		}
	}
	
	@Test void testParameterLimits0() {
		assertThrows(RuntimeException.class, () -> {
			freeFlowSpeedDistr.getValue(-0.1);
		});
	}

	@Test void testParameterLimits1() {
		assertThrows(RuntimeException.class, () -> {
			freeFlowSpeedDistr.getValue(1.05);
		});
	}
	
	@Test void testValue0() {
		double expected = 72.0815217391304; // from a spreadsheet
		double actual = freeFlowSpeedDistr.getValue(0.85);
		assertEquals(expected, actual, 0.0001);
	}
	
	@Test void testValue1() {
		double expected = 20.;
		double actual = laneChangeDistanceDistr.getValue(0.95);
		assertEquals(expected, actual, 0.0001);
	}
	
	@Test void testValue2() {
		double expected = 30.;
		double actual = irregularBinsDistr.getValue(0.1);
		assertEquals(expected, actual, 0.0001);
	}
	
	@Test void testValue3() {
		double expected = 70.;
		double actual = irregularBinsDistr.getValue(0.3);
		assertEquals(expected, actual, 0.0001);
	}
	
	@Test void testValue4() {
		double expected = 100.;
		double actual = irregularBinsDistr.getValue(0.4999999);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testValue5() {
		double expected = 110.;
		double actual = irregularBinsDistr.getValue(0.5000001);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testValue6() {
		double expected = 164.;
		double actual = irregularBinsDistr.getValue(0.8);
		assertEquals(expected, actual, 0.0001);
	}
}
