package com.github.kjburns.traffic_simulation.parameters;

import org.junit.runner.RunWith;
import org.junit.runners.Suite;
import org.junit.runners.Suite.SuiteClasses;

@RunWith(Suite.class)
@SuiteClasses({
	NormalDistributionTruncatableTest.class,
	NormalDistributionTruncatableXmlTest.class,
})
public class DistributionTests {

}
