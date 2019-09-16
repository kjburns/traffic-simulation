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

import com.github.kjburns.traffic_simulation.main.UnitsEnum;
import com.github.kjburns.traffic_simulation.parameters.VehicleModel.Trailer;
import com.github.kjburns.traffic_simulation.parameters.VehicleModel.VehicleUnit;

class VehicleModelImplTest {
	private final VehicleModel modelWithoutTrailer;
	private final VehicleModel modelWithOneTrailer;
	private final VehicleModel modelWithTwoTrailers;
	
	public VehicleModelImplTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/VehicleModelTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("vehicle-model");
			modelWithoutTrailer = new VehicleModelImpl((Element)nodes.item(0), UnitsEnum.METERS);
			modelWithOneTrailer = new VehicleModelImpl((Element)nodes.item(1), UnitsEnum.METERS);
			modelWithTwoTrailers = new VehicleModelImpl((Element)nodes.item(2), UnitsEnum.METERS);
		}
	}
	
	@Test void testGetTotalLengthOneVehicle() {
		final double expected = 4.534;
		final double actual = modelWithoutTrailer.getTotalLength();
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testGetTotalLengthTwoVehicles() {
		final double expected = 10.0226;
		final double actual = modelWithOneTrailer.getTotalLength();
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testGetTotalLengthThreeVehicles() {
		final double expected = 28.;
		final double actual = modelWithTwoTrailers.getTotalLength();
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testGetMaximumWidthOneVehicle() {
		final double expected = 1.823;
		final double actual = modelWithoutTrailer.getMaximumWidth();
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testGetMaximumWidthThreeVehicles() {
		final double expected = 2.5;
		final double actual = modelWithTwoTrailers.getMaximumWidth();
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testGetLeadVehicleOneUnit() {
		assertTrue(modelWithoutTrailer.getLeadVehicle().getName().indexOf("Focus") != -1);
	}

	@Test void testGetLeadVehicleThreeUnits() {
		assertTrue(modelWithTwoTrailers.getLeadVehicle().getName().indexOf("Double-") != -1);
	}
	
	@Test void testDistanceFromFrontOneUnit() {
		final double expected = 0.;
		final double actual = modelWithoutTrailer.getDistanceFromFront(modelWithoutTrailer.getLeadVehicle());
		
		assertEquals(expected, actual, 0.0001);
	}
	
	@Test void testDistanceFromFrontTwoUnits() {
		final VehicleUnit lead = modelWithOneTrailer.getLeadVehicle();
		final Trailer trailer = lead.getTrailer_rNull();
		final double expected = 5.73;
		final double actual = modelWithOneTrailer.getDistanceFromFront(trailer);
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testDistanceFromFrontThreeUnits0() {
		final VehicleUnit lead = modelWithTwoTrailers.getLeadVehicle();
		final Trailer trailer = lead.getTrailer_rNull().getTrailer_rNull();
		final double expected = 16.;
		final double actual = modelWithTwoTrailers.getDistanceFromFront(trailer);
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testDistanceFromFrontThreeUnits1() {
		final VehicleUnit lead = modelWithTwoTrailers.getLeadVehicle();
		final double expected = 0.;
		final double actual = modelWithTwoTrailers.getDistanceFromFront(lead);
		
		assertEquals(expected, actual, 0.0001);
	}
	
	@Test void testStream() {
		final long expected = 3;
		final long actual = modelWithTwoTrailers.unitsStream().count();
		
		assertEquals(expected, actual);
	}
}
