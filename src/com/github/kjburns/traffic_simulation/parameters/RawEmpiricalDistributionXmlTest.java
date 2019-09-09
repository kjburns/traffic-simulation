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

class RawEmpiricalDistributionXmlTest {
	private final Distribution<Double> testDistribution;
	
	public RawEmpiricalDistributionXmlTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/RawEmpiricalDistributionTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("raw-empirical-distribution");
			testDistribution = RealNumberDistributionFactory.createDistribution((Element)nodes.item(0));
		}
	}

	@Test void testParameterLimits0() {
		assertThrows(RuntimeException.class, () -> {
			testDistribution.getValue(-0.5);
		});
	}

	@Test void testParameterLimits1() {
		assertThrows(RuntimeException.class, () -> {
			testDistribution.getValue(1.5);
		});
	}
	
	@Test void testValueLeftEdgeCase() {
		double expected = 45.;
		double actual = testDistribution.getValue(0.05);
		assertEquals(expected, actual, 0.001);
	}
	@Test void testValueRightEdgeCase() {
		double expected = 65.;
		double actual = testDistribution.getValue(0.99);
		assertEquals(expected, actual, 0.001);
	}
	@Test void testValueMidBinCase() {
		double expected = 52.;
		double actual = testDistribution.getValue(0.38);
		assertEquals(expected, actual, 0.001);
	}
	@Test void testValueBinEdgeCase() {
		double expected = 50.;
		double actual = testDistribution.getValue(0.3);
		assertEquals(expected, actual, 0.001);
	}
}
